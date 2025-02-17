# Copyright (C) 2020  GreenWaves Technologies, SAS

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from graph.types import SSDDetectorParameters
from quantization.kernels.kernel_base import (KernelBase, params_type,
                                              qrec_type)
from quantization.multiplicative.mulbias import set_ssd_scales
from quantization.new_qrec import QRec
from utils.exp_17_15 import exp_fp_17_15
from utils.at_norm import at_norm
from utils.ssd_utils import (CNTX_IDX, CNTY_IDX, H_IDX, W_IDX, XMAX_IDX,
                             XMIN_IDX, YMAX_IDX, YMIN_IDX, convert_cors2cnts,
                             rect_intersect_area, rect_union_area)


@params_type(SSDDetectorParameters)
@qrec_type('scaled')
class SSDDetectorSymmetric(KernelBase):
    @classmethod
    def execute(cls, params,
                in_tensors,
                qrec: QRec,
                **kwargs):
        in_tensors = qrec.prepare_inputs(params, in_tensors, ktype="symmetric")
        offsets = in_tensors[0]
        scores = in_tensors[1]
        anchors = in_tensors[2]
        # decoded_bboxes: Q14
        # valid_scores: Q7
        anchors_type = "centers"
        if anchors_type == 'centers':
            anchors_cnts = anchors
        else:
            anchors_cnts = convert_cors2cnts(anchors)
        set_ssd_scales(qrec, params)
        scores_q = qrec.in_qs[1]
        score_threshold = scores_q.quantize(params.nms_score_threshold)
        decoded_bboxes = []
        for i in range(scores.shape[0]):
            for j in range(scores.shape[1]):
                if len(decoded_bboxes) > params.max_bb_before_nms:
                    break
                if scores[i, j] <= score_threshold:
                    continue
                offset = offsets[i]
                anchor = anchors[i]
                #  xcnt, ycnt --> Q14
                #  xcnt = (So*O * Sa*Aw)/params.x_scale + Sa*Ax = So*Sa/params.x_scale (O*Aw + x_scale/So * Ax) =
                #           (scale_x * (O*Aw + (scale_x_anc*Ax)>>scale_x_ancNorm))>>scale_xNorm =
                #           at_norm(scale_x*(O*Aw + at_norm(scale_x_anc*Ax, scale_x_ancNorm)), scale_xNorm)
                xcenter = qrec.cache['scale_x_q'].apply_scales(
                    np.multiply(offset[CNTX_IDX], anchor[W_IDX], dtype=np.int32) +
                    qrec.cache['scale_x_anc_q'].apply_scales(anchor[CNTX_IDX])
                )
                ycenter = qrec.cache['scale_y_q'].apply_scales(
                    np.multiply(offset[CNTY_IDX], anchor[H_IDX], dtype=np.int32) +
                    qrec.cache['scale_y_anc_q'].apply_scales(anchor[CNTY_IDX])
                )

                #  half_h, half_w --> Q14
                #  half_h = exp(So*Off / params.h_scale) * Sa*A = Sa/So * exp(So/params.h_scale *O) * A =
                #           (scale_ao * (A* exp17.15(scale_h*O<<15-scale_hNorm))>>scale_aoNorm) =
                #           at_norm(scale_ao*(A*exp17.15(scale_h*O<<15-scale_hNorm)), scale_aoNorm)
                norm_h = 15 - qrec.cache['scale_h_q'].qnorms
                norm_w = 15 - qrec.cache['scale_w_q'].qnorms
                exp_h = exp_fp_17_15(np.multiply(offset[H_IDX], int(
                    qrec.cache['scale_h_q'].qbiases), dtype=np.int32) << norm_h)
                exp_w = exp_fp_17_15(np.multiply(offset[W_IDX], int(
                    qrec.cache['scale_w_q'].qbiases), dtype=np.int32) << norm_w)
                half_h = qrec.cache['scale_ao_q'].apply_scales(np.multiply(
                    exp_h, anchor[H_IDX], dtype=np.int32)) >> 1
                half_w = qrec.cache['scale_ao_q'].apply_scales(np.multiply(
                    exp_w, anchor[W_IDX], dtype=np.int32)) >> 1

                decoded_bboxes.append({
                                       "bbox": [ycenter-half_h, xcenter-half_w, ycenter+half_h, xcenter+half_w],
                                       "score": scores[i, j],
                                       "class": j,
                                       "alive": True
                                      })

        # Bubble sort to sort the scores
        changed = True
        while changed:
            changed = False
            for i in range(len(decoded_bboxes)-1):
                if decoded_bboxes[i]['score'] < decoded_bboxes[i+1]['score']:
                    temp = decoded_bboxes[i]
                    decoded_bboxes[i] = decoded_bboxes[i+1]
                    decoded_bboxes[i+1] = temp
                    changed = True

        # NMS
        for idx in range(len(decoded_bboxes)):
            for idx_int in range(idx+1, len(decoded_bboxes)):
                if (not decoded_bboxes[idx_int]['alive']) or (decoded_bboxes[idx]['class'] != decoded_bboxes[idx_int]['class']):
                    continue
                intersection = rect_intersect_area(decoded_bboxes[idx]['bbox'], decoded_bboxes[idx_int]['bbox'])
                union = rect_union_area(decoded_bboxes[idx]['bbox'], decoded_bboxes[idx_int]['bbox'])
                if intersection >= at_norm(scores_q.quantize(params.nms_iou_threshold) * union, 7):
                    decoded_bboxes[idx_int]['alive'] = False

        out_boxes = np.zeros((params.max_detections, 4), dtype=qrec.out_qs[0].dtype)
        out_classes = np.zeros(params.max_detections, dtype=qrec.out_qs[1].dtype)
        out_scores = np.zeros(params.max_detections, dtype=qrec.out_qs[2].dtype)
        out_idx = 0
        for i in range(len(decoded_bboxes)):
            if out_idx >= params.max_detections:
                break
            bbox = decoded_bboxes[i]
            if bbox['alive']:
                out_boxes[out_idx] = bbox['bbox']
                out_classes[out_idx] = bbox['class']
                out_scores[out_idx] = bbox['score']
                out_idx += 1
        # decoded_bboxes, valid_scores = cls.decoder(
        #     params, qrec, offsets, anchors, scores, anchors_type='centers')
        # out_boxes, out_scores, out_classes = cls.nms(params, qrec, decoded_bboxes, valid_scores)
        # out_count = np.array([sum(out_classes != 0)])
        return qrec.get_outputs(params, [out_boxes, out_classes, out_scores], ktype="symmetric")

    # @classmethod
    # def decoder(cls, params, qrec, offsets, anchors, scores, anchors_type='centers'):
    #     if anchors_type == 'centers':
    #         anchors_cnts = anchors
    #     else:
    #         anchors_cnts = convert_cors2cnts(anchors)

    #     out_boxes_q = qrec.out_qs[0]

    #     scores_q = qrec.in_qs[1]
    #     score_threshold = scores_q.quantize(params.nms_score_threshold)

    #     # keep only the offsets with score > threshold
    #     bboxes_indices = np.arange(offsets.shape[0])
    #     valid_indices = bboxes_indices[np.any(scores > score_threshold, axis=1)]
    #     valid_scores = scores[valid_indices]
    #     valid_offsets = offsets[valid_indices]
    #     valid_anchors = anchors_cnts[valid_indices]

    #     set_ssd_scales(qrec, params)
    #     #  xcnt, ycnt --> Q14
    #     #  xcnt = (So*O * Sa*Aw)/params.x_scale + Sa*Ax = So*Sa/params.x_scale (O*Aw + x_scale/So * Ax) =
    #     #           (scale_x * (O*Aw + (scale_x_anc*Ax)>>scale_x_ancNorm))>>scale_xNorm =
    #     #           at_norm(scale_x*(O*Aw + at_norm(scale_x_anc*Ax, scale_x_ancNorm)), scale_xNorm)
    #     xcenter = qrec.cache['scale_x_q'].apply_scales(
    #         np.multiply(valid_offsets[:, CNTX_IDX], valid_anchors[:, W_IDX], dtype=np.int32) +
    #         qrec.cache['scale_x_anc_q'].apply_scales(valid_anchors[:, CNTX_IDX])
    #     )
    #     ycenter = qrec.cache['scale_y_q'].apply_scales(
    #         np.multiply(valid_offsets[:, CNTY_IDX], valid_anchors[:, H_IDX], dtype=np.int32) +
    #         qrec.cache['scale_y_anc_q'].apply_scales(valid_anchors[:, CNTY_IDX])
    #     )

    #     #  half_h, half_w --> Q14
    #     #  half_h = exp(So*Off / params.h_scale) * Sa*A = Sa/So * exp(So/params.h_scale *O) * A =
    #     #           (scale_ao * (A* exp17.15(scale_h*O<<15-scale_hNorm))>>scale_aoNorm) =
    #     #           at_norm(scale_ao*(A*exp17.15(scale_h*O<<15-scale_hNorm)), scale_aoNorm)
    #     norm_h = 15 - qrec.cache['scale_h_q'].qnorms
    #     norm_w = 15 - qrec.cache['scale_w_q'].qnorms
    #     exp_h = exp_fp_17_15(np.multiply(valid_offsets[:, H_IDX], int(
    #         qrec.cache['scale_h_q'].qbiases), dtype=np.int32) << norm_h)
    #     exp_w = exp_fp_17_15(np.multiply(valid_offsets[:, W_IDX], int(
    #         qrec.cache['scale_w_q'].qbiases), dtype=np.int32) << norm_w)
    #     half_h = qrec.cache['scale_ao_q'].apply_scales(np.multiply(
    #         exp_h, valid_anchors[:, H_IDX], dtype=np.int32)) >> 1
    #     half_w = qrec.cache['scale_ao_q'].apply_scales(np.multiply(
    #         exp_w, valid_anchors[:, W_IDX], dtype=np.int32)) >> 1

    #     # min-max or corners format: required for nms
    #     decoded_anchors = np.zeros_like(valid_anchors, dtype=out_boxes_q.dtype)
    #     decoded_anchors[:, YMIN_IDX] = ycenter - half_h
    #     decoded_anchors[:, YMAX_IDX] = ycenter + half_h
    #     decoded_anchors[:, XMIN_IDX] = xcenter - half_w
    #     decoded_anchors[:, XMAX_IDX] = xcenter + half_w
    #     return decoded_anchors, valid_scores

    # @classmethod
    # def nms(cls, params, qrec, decoded_bboxes, valid_scores):
    #     scores_q = qrec.in_qs[1]
    #     score_threshold = scores_q.quantize(params.nms_score_threshold)
    #     # loop over classes apart the background
    #     num_classes = valid_scores.shape[1]
    #     out_boxes = []
    #     out_scores = []
    #     out_classes = []
    #     for class_idx in range(1, num_classes):
    #         class_scores = valid_scores[:, class_idx]
    #         # default anchors indices before appplying any sort
    #         bboxes_indices = np.arange(decoded_bboxes.shape[0])
    #         # apply confidence threshold
    #         valid_scores_indices = bboxes_indices[class_scores > score_threshold]
    #         class_scores = class_scores[valid_scores_indices]

    #         # sort the confidences freater than the confidence threshold
    #         args = np.argsort(-class_scores)  # sort the confidences and
    #         inds = valid_scores_indices[args]     # back to the original indices
    #         sorted_bboxes = decoded_bboxes[inds]
    #         sorted_scores = class_scores[args]
    #         liveness = [True] * sorted_bboxes.shape[0]
    #         for i, box_a in enumerate(sorted_bboxes):
    #             if not liveness[i]:
    #                 continue
    #             for j in range(i+1, len(sorted_bboxes)):
    #                 box_b = sorted_bboxes[j]
    #                 intersection = rect_intersect_area(box_a, box_b)
    #                 union = rect_union_area(box_a, box_b)
    #                 if intersection >= at_norm(scores_q.quantize(params.nms_iou_threshold) * union, 7):
    #                     # iou > threshold ->
    #                     # discard second box which is dominated by the first because they are sorted
    #                     liveness[j] = False
    #         if sum(liveness) > 0:
    #             out_boxes.append(sorted_bboxes[liveness])
    #             out_scores.append(sorted_scores[liveness])
    #             out_classes.append([class_idx] * sum(liveness))
    #     if len(out_boxes) > 0:
    #         out_boxes = np.concatenate(out_boxes)
    #         out_classes = np.concatenate(out_classes)
    #         out_scores = np.concatenate(out_scores)
    #         # keep only the max_detection most probables
    #         args = np.argsort(out_scores)[::-1]
    #         if len(args) < params.max_detections:
    #             return np.pad(out_boxes[args], ((0, params.max_detections-len(args)), (0, 0)), 'constant'), \
    #                 np.pad(out_scores[args], (0, params.max_detections-len(args)), 'constant'), \
    #                 np.pad(out_classes[args], (0, params.max_detections-len(args)), 'constant')
    #         args = args[:params.max_detections]
    #         return out_boxes[args], out_scores[args], out_classes[args]
    #     return np.zeros((params.max_detections, 4)), np.zeros(params.max_detections), np.zeros(params.max_detections)
