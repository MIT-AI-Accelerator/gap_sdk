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

import numpy as np
from generation.at_types.at_params import NO_ACTIVATION, gen_active_at_params
from generation.at_types.gen_ctrl import GenCtrl
from generation.code_block import CodeBlock
from generation.generator_decorators import QREC_MULT8, generation_function
from graph.types import ActivationFusionBase, MatrixMulParameters

from ..autotiler_kernel import AutotilerKernel

LOG = logging.getLogger("nntool." + __name__)

MAT_VECT_MUL_OPER = "KOP_MATVECTMUL"

def validate_kernel(node):
    shape1 = node.in_dims[0]
    shape2 = node.in_dims[1]
    if len(shape1) != 3 or len(shape1) != len(shape2):
        return None
    if np.prod(shape1) == shape2[0]:
        return 0
    if np.prod(shape1) == shape2[0]:
        return 1
    return None

@generation_function("kernels", (MatrixMulParameters, ActivationFusionBase), qrec_types=(QREC_MULT8, ))
def mat_vect_mult_kernel_generator(gen, node, qrec, in_eparams, out_eparams, cname):
    del in_eparams, out_eparams, qrec
    if isinstance(node, ActivationFusionBase):
        cnodes = node.contained_nodes()
        if isinstance(cnodes[0], MatrixMulParameters) and validate_kernel(cnodes[0]) is not None:
            gen.kernels.append(MatVectMulKernel(node.name, cname, cnodes[0], cnodes[1],
                                                at_ver=gen.opts['at_ver'], force_relu=gen.force_relu))
            return True
        return False
    elif validate_kernel(node) is not None:
        gen.kernels.append(MatVectMulKernel(node.name, cname, node, None, at_ver=gen.opts['at_ver'],
                                            force_relu=gen.force_relu))
        return True
    return False


def gen_mat_vect_mul_sq8(code_block, cname, ctrl, feat, width, height, act_oper):
    code_block.write('CNN_TensorVectMultAct_SQ8("{}", {}, {}, {}, {}, {}, {});'.format(cname, ctrl,
                                                                                       feat, width,
                                                                                       height,
                                                                                       MAT_VECT_MUL_OPER,
                                                                                       act_oper))


class MatVectMulKernel(AutotilerKernel):
    def __init__(self, node_name, cname, tens_vect_mul_params, act_params, at_ver=3, gen_ctrl=None, force_relu=True):
        if gen_ctrl is None:
            self.gen_ctrl = gen_ctrl = GenCtrl(None, cname=cname)
        else:
            gen_ctrl.cname = cname
            self.gen_ctrl = gen_ctrl

        self.cname = cname
        self.node_name = node_name
        self.at_ver = at_ver

        if act_params is not None:
            self.at_act_params = gen_active_at_params(
                act_params, force_relu=force_relu)
        else:
            self.at_act_params = NO_ACTIVATION

        self.tens_vect_mul_params = tens_vect_mul_params
        if tens_vect_mul_params.in_dims[0] == tens_vect_mul_params.in_dims[1]:
            # broadcast matrix * matrix
            self.feat_dim = tens_vect_mul_params.in_dims[0].size()
            self.height = 1
            self.width = 1
        else:
            # probably need more logic here to handle
            dimensions = tens_vect_mul_params.in_dims[0]
            self.feat_dim = dimensions[0]
            self.width = dimensions[1]
            self.height = dimensions[2]

    def code(self, code_block=None):
        if code_block is None:
            code_block = CodeBlock()

        code_block.comment("generator for {}", self.node_name)

        if not self.gen_ctrl.is_unmodified:
            self.gen_ctrl.gen_ctrl_decl(code_block)
            gen_ctrl = self.gen_ctrl.ctrl_name
        else:
            gen_ctrl = "0"

        gen_mat_vect_mul_sq8(code_block, self.cname, gen_ctrl, self.feat_dim,
                             self.width, self.height, self.at_act_params.ReLUOper)

        return code_block
