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

import logging

from graph.dim import Dim

from .base import Parameters, SensitiveToOrder, cls_op_name, nargs

LOG = logging.getLogger("nntool." + __name__)

SSD_INPUT_NAMES = ['boxes_offsets', 'scores', 'anchors']

@cls_op_name('ssd_detector')
@nargs(SSD_INPUT_NAMES)
class SSDDetectorParameters(Parameters, SensitiveToOrder):

    INPUT_NAMES = SSD_INPUT_NAMES

    def __init__(self, *args, parameters=None, **kwargs):
        super(SSDDetectorParameters, self).__init__(*args, **kwargs)
        self._parameters = parameters
        self._parameters["use_exp_for_wh_decode"] = True
        self.decoder_config = {'using_json_config': {'INCLUDE': False, 'json_config_path': ''},
                               'using_pipeline_config': {'INCLUDE': False, 'pipeline_config_path': ''},
                               'using_params': {'INCLUDE': True, 'params': self._parameters}}

        self.nms_config = {'using_json_config': {'INCLUDE': False, 'json_config_path': ''},
                           'using_pipeline_config': {'INCLUDE': False, 'pipeline_config_path': ''},
                           'using_params': {'INCLUDE': True, 'params': self._parameters}}

    def __call__(self, *args, **kwargs):
        noderef = super(SSDDetectorParameters, self).__call__(*args, **kwargs)
        return tuple(NNNodeRef(self, i, noderef.ref[1]) for i in range(3))

    def get_parameter_size(self):
        return 0

    @property
    def can_equalize(self):
        return False

    @property
    def x_scale(self):
        return self._parameters['x_scale']

    @property
    def y_scale(self):
        return self._parameters['y_scale']

    @property
    def w_scale(self):
        return self._parameters['w_scale']

    @property
    def h_scale(self):
        return self._parameters['h_scale']

    @property
    def nms_score_threshold(self):
        return self._parameters['nms_score_threshold']

    @nms_score_threshold.setter
    def nms_score_threshold(self, val):
        self._parameters['nms_score_threshold'] = val

    @property
    def max_bb_before_nms(self):
        return self._parameters['max_bb_before_nms']

    @max_bb_before_nms.setter
    def max_bb_before_nms(self, val):
        self._parameters['max_bb_before_nms'] = val

    @property
    def use_exp_for_wh_decode(self):
        return self._parameters['use_exp_for_wh_decode']

    @use_exp_for_wh_decode.setter
    def use_exp_for_wh_decode(self, val):
        self._parameters['use_exp_for_wh_decode'] = val

    @property
    def nms_iou_threshold(self):
        return self._parameters['nms_iou_threshold']

    @property
    def max_detections(self):
        return self._parameters['max_detections']

    @property
    def max_classes_per_detection(self):
        return self._parameters['max_classes_per_detection']

    def get_output_size(self, in_dims):
        num_detected_boxes = self._parameters['max_detections'] * \
            self._parameters['max_classes_per_detection']
        return [
            Dim(shape=[num_detected_boxes, 4], is_ordered=True),
            Dim(shape=[num_detected_boxes], is_ordered=True),
            Dim(shape=[num_detected_boxes], is_ordered=True),
            Dim(shape=[num_detected_boxes], is_ordered=True),
        ]

    def __str__(self):
        return "{} SCORE_THR {:.2f} IOU_THR {:.2f}".format(
            self.at_options,
            self.nms_score_threshold,
            self.nms_iou_threshold
        )
