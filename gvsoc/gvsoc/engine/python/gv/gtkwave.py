#
# Copyright (C) 2020 GreenWaves Technologies, SAS, ETH Zurich and
#                    University of Bologna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# 
# Authors: Germain Haugou, GreenWaves Technologies (germain.haugou@greenwaves-technologies.com)
#

from os import listdir
from os.path import isfile, join, isdir
import os.path

import json_tools as js
import pulp_config

import gtkw_new

gtkw_colors = [
"alice blue",
"AliceBlue",
"antique white",
"AntiqueWhite",
"AntiqueWhite1",
"AntiqueWhite2",
"AntiqueWhite3",
"AntiqueWhite4",
"aquamarine",
"aquamarine1",
"aquamarine2",
"aquamarine3",
"aquamarine4",
"azure",
"azure1",
"azure2",
"azure3",
"azure4",
"beige",
"bisque",
"bisque1",
"bisque2",
"bisque3",
"bisque4",
"black",
"blanched almond",
"BlanchedAlmond",
"blue",
"blue violet",
"blue1",
"blue2",
"blue3",
"blue4",
"BlueViolet",
"brown",
"brown1",
"brown2",
"brown3",
"brown4",
"burlywood",
"burlywood1",
"burlywood2",
"burlywood3",
"burlywood4",
"cadet blue",
"CadetBlue",
"CadetBlue1",
"CadetBlue2",
"CadetBlue3",
"CadetBlue4",
"chartreuse",
"chartreuse1",
"chartreuse2",
"chartreuse3",
"chartreuse4",
"chocolate",
"chocolate1",
"chocolate2",
"chocolate3",
"chocolate4",
"coral",
"coral1",
"coral2",
"coral3",
"coral4",
"cornflower blue",
"CornflowerBlue",
"cornsilk",
"cornsilk1",
"cornsilk2",
"cornsilk3",
"cornsilk4",
"cyan",
"cyan1",
"cyan2",
"cyan3",
"cyan4",
"dark blue",
"dark cyan",
"dark goldenrod",
"dark gray",
"dark green",
"dark grey",
"dark khaki",
"dark magenta",
"dark olive green",
"dark orange",
"dark orchid",
"dark red",
"dark salmon",
"dark sea green",
"dark slate blue",
"dark slate gray",
"dark slate grey",
"dark turquoise",
"dark violet",
"DarkBlue",
"DarkCyan",
"DarkGoldenrod",
"DarkGoldenrod1",
"DarkGoldenrod2",
"DarkGoldenrod3",
"DarkGoldenrod4",
"DarkGray",
"DarkGreen",
"DarkGrey",
"DarkKhaki",
"DarkMagenta",
"DarkOliveGreen",
"DarkOliveGreen1",
"DarkOliveGreen2",
"DarkOliveGreen3",
"DarkOliveGreen4",
"DarkOrange",
"DarkOrange1",
"DarkOrange2",
"DarkOrange3",
"DarkOrange4",
"DarkOrchid",
"DarkOrchid1",
"DarkOrchid2",
"DarkOrchid3",
"DarkOrchid4",
"DarkRed",
"DarkSalmon",
"DarkSeaGreen",
"DarkSeaGreen1",
"DarkSeaGreen2", 
"DarkSeaGreen3",
"DarkSeaGreen4",
"DarkSlateBlue",
"DarkSlateGray",
"DarkSlateGray1",
"DarkSlateGray2",
"DarkSlateGray3",
"DarkSlateGray4",
"DarkSlateGrey",
"DarkTurquoise",
"DarkViolet",
"deep pink",
"deep sky blue",
"DeepPink",
"DeepPink1",
"DeepPink2",
"DeepPink3",
"DeepPink4",
"DeepSkyBlue",
"DeepSkyBlue1",
"DeepSkyBlue2",
"DeepSkyBlue3",
"DeepSkyBlue4",
"dim gray",
"dim grey",
"DimGray",
"DimGrey",
"dodger blue",
"DodgerBlue",
"DodgerBlue1",
"DodgerBlue2",
"DodgerBlue3",
"DodgerBlue4",
"firebrick",
"firebrick1",
"firebrick2",
"firebrick3",
"firebrick4",
"floral white",
"FloralWhite",
"forest green",
"ForestGreen",
"gainsboro",
"ghost white",
"GhostWhite",
"gold",
"gold1",
"gold2",
"gold3",
"gold4",
"goldenrod",
"goldenrod1",
"goldenrod2",
"goldenrod3",
"goldenrod4",
"gray",
"gray0",
"gray1",
"gray10",
"gray100",
"gray11",
"gray12",
"gray13",
"gray14",
"gray15",
"gray16",
"gray17",
"gray18",
"gray19",
"gray2",
"gray20",
"gray21",
"gray22",
"gray23",
"gray24",
"gray25",
"gray26",
"gray27",
"gray28",
"gray29",
"gray3",
"gray30",
"gray31",
"gray32",
"gray33",
"gray34",
"gray35",
"gray36",
"gray37",
"gray38",
"gray39",
"gray4",
"gray40",
"gray41",
"gray42",
"gray43",
"gray44",
"gray45",
"gray46",
"gray47",
"gray48",
"gray49",
"gray5",
"gray50",
"gray51",
"gray52",
"gray53",
"gray54",
"gray55",
"gray56",
"gray57",
"gray58",
"gray59",
"gray6",
"gray60",
"gray61",
"gray62",
"gray63",
"gray64",
"gray65",
"gray66",
"gray67",
"gray68",
"gray69",
"gray7",
"gray70",
"gray71",
"gray72",
"gray73",
"gray74",
"gray75",
"gray76",
"gray77",
"gray78",
"gray79",
"gray8",
"gray80",
"gray81",
"gray82",
"gray83",
"gray84",
"gray85",
"gray86",
"gray87",
"gray88",
"gray89",
"gray9",
"gray90",
"gray91",
"gray92",
"gray93",
"gray94",
"gray95",
"gray96",
"gray97",
"gray98",
"gray99",
"green",
"green yellow",
"green1",
"green2",
"green3",
"green4",
"GreenYellow",
"grey",
"grey0",
"grey1",
"grey10",
"grey100",
"grey11",
"grey12",
"grey13",
"grey14",
"grey15",
"grey16",
"grey17",
"grey18",
"grey19",
"grey2",
"grey20",
"grey21",
"grey22",
"grey23",
"grey24",
"grey25",
"grey26",
"grey27",
"grey28",
"grey29",
"grey3",
"grey30",
"grey31",
"grey32",
"grey33",
"grey34",
"grey35",
"grey36",
"grey37",
"grey38",
"grey39",
"grey4",
"grey40",
"grey41",
"grey42",
"grey43",
"grey44",
"grey45",
"grey46",
"grey47",
"grey48",
"grey49",
"grey5",
"grey50",
"grey51",
"grey52",
"grey53",
"grey54",
"grey55",
"grey56",
"grey57",
"grey58",
"grey59",
"grey6",
"grey60",
"grey61",
"grey62",
"grey63",
"grey64",
"grey65",
"grey66",
"grey67",
"grey68",
"grey69",
"grey7",
"grey70",
"grey71",
"grey72",
"grey73",
"grey74",
"grey75",
"grey76",
"grey77",
"grey78",
"grey79",
"grey8",
"grey80",
"grey81",
"grey82",
"grey83",
"grey84",
"grey85",
"grey86",
"grey87",
"grey88",
"grey89",
"grey9",
"grey90",
"grey91",
"grey92",
"grey93",
"grey94",
"grey95",
"grey96",
"grey97",
"grey98",
"grey99",
"honeydew",
"honeydew1",
"honeydew2",
"honeydew3",
"honeydew4",
"hot pink",
"HotPink",
"HotPink1",
"HotPink2",
"HotPink3",
"HotPink4",
"indian red",
"IndianRed",
"IndianRed1",
"IndianRed2",
"IndianRed3",
"IndianRed4",
"ivory",
"ivory1",
"ivory2",
"ivory3",
"ivory4",
"khaki",
"khaki1",
"khaki2",
"khaki3",
"khaki4",
"lavender",
"lavender blush",
"LavenderBlush",
"LavenderBlush1",
"LavenderBlush2",
"LavenderBlush3",
"LavenderBlush4",
"lawn green",
"LawnGreen",
"lemon chiffon",
"LemonChiffon",
"LemonChiffon1",
"LemonChiffon2",
"LemonChiffon3",
"LemonChiffon4",
"light blue",
"light coral",
"light cyan",
"light goldenrod",
"light goldenrod yellow",
"light gray",
"light green",
"light grey",
"light pink",
"light salmon",
"light sea green",
"light sky blue",
"light slate blue",
"light slate gray",
"light slate grey",
"light steel blue",
"light yellow",
"LightBlue",
"LightBlue1",
"LightBlue2",
"LightBlue3",
"LightBlue4",
"LightCoral",
"LightCyan",
"LightCyan1",
"LightCyan2",
"LightCyan3",
"LightCyan4",
"LightGoldenrod",
"LightGoldenrod1",
"LightGoldenrod2",
"LightGoldenrod3",
"LightGoldenrod4",
"LightGoldenrodYellow",
"LightGray",
"LightGreen",
"LightGrey",
"LightPink",
"LightPink1",
"LightPink2",
"LightPink3",
"LightPink4",
"LightSalmon",
"LightSalmon1",
"LightSalmon2",
"LightSalmon3",
"LightSalmon4",
"LightSeaGreen",
"LightSkyBlue",
"LightSkyBlue1",
"LightSkyBlue2",
"LightSkyBlue3",
"LightSkyBlue4",
"LightSlateBlue",
"LightSlateGray",
"LightSlateGrey",
"LightSteelBlue",
"LightSteelBlue1",
"LightSteelBlue2",
"LightSteelBlue3",
"LightSteelBlue4",
"LightYellow",
"LightYellow1",
"LightYellow2",
"LightYellow3",
"LightYellow4",
"lime green",
"LimeGreen",
"linen",
"magenta",
"magenta1",
"magenta2",
"magenta3",
"magenta4",
"maroon",
"maroon1",
"maroon2",
"maroon3",
"maroon4",
"medium aquamarine",
"medium blue",
"medium orchid",
"medium purple",
"medium sea green",
"medium slate blue",
"medium spring green",
"medium turquoise",
"medium violet red",
"MediumAquamarine",
"MediumBlue",
"MediumOrchid",
"MediumOrchid1",
"MediumOrchid2",
"MediumOrchid3",
"MediumOrchid4",
"MediumPurple",
"MediumPurple1",
"MediumPurple2",
"MediumPurple3",
"MediumPurple4",
"MediumSeaGreen",
"MediumSlateBlue",
"MediumSpringGreen",
"MediumTurquoise",
"MediumVioletRed",
"midnight blue",
"MidnightBlue",
"mint cream",
"MintCream",
"misty rose",
"MistyRose",
"MistyRose1",
"MistyRose2",
"MistyRose3",
"MistyRose4",
"moccasin",
"navajo white",
"NavajoWhite",
"NavajoWhite1",
"NavajoWhite2",
"NavajoWhite3",
"NavajoWhite4",
"navy",
"navy blue",
"NavyBlue",
"old lace",
"OldLace",
"olive drab",
"OliveDrab",
"OliveDrab1",
"OliveDrab2",
"OliveDrab3",
"OliveDrab4",
"orange",
"orange red",
"orange1",
"orange2",
"orange3",
"orange4",
"OrangeRed",
"OrangeRed1",
"OrangeRed2",
"OrangeRed3",
"OrangeRed4",
"orchid",
"orchid1",
"orchid2",
"orchid3",
"orchid4",
"pale goldenrod",
"pale green",
"pale turquoise",
"pale violet red",
"PaleGoldenrod",
"PaleGreen",
"PaleGreen1",
"PaleGreen2",
"PaleGreen3",
"PaleGreen4",
"PaleTurquoise",
"PaleTurquoise1",
"PaleTurquoise2",
"PaleTurquoise3",
"PaleTurquoise4",
"PaleVioletRed",
"PaleVioletRed1",
"PaleVioletRed2",
"PaleVioletRed3",
"PaleVioletRed4",
"papaya whip",
"PapayaWhip",
"peach puff",
"PeachPuff",
"PeachPuff1",
"PeachPuff2",
"PeachPuff3",
"PeachPuff4",
"peru",
"pink",
"pink1",
"pink2",
"pink3",
"pink4",
"plum",
"plum1",
"plum2",
"plum3",
"plum4",
"powder blue",
"PowderBlue",
"purple",
"purple1",
"purple2",
"purple3",
"purple4",
"red",
"red1",
"red2",
"red3",
"red4",
"rosy brown",
"RosyBrown",
"RosyBrown1",
"RosyBrown2",
"RosyBrown3",
"RosyBrown4",
"royal blue",
"RoyalBlue",
"RoyalBlue1",
"RoyalBlue2",
"RoyalBlue3",
"RoyalBlue4",
"saddle brown",
"SaddleBrown",
"salmon",
"salmon1",
"salmon2",
"salmon3",
"salmon4",
"sandy brown",
"SandyBrown",
"sea green",
"SeaGreen",
"SeaGreen1",
"SeaGreen2",
"SeaGreen3",
"SeaGreen4",
"seashell",
"seashell1",
"seashell2",
"seashell3",
"seashell4",
"sienna",
"sienna1",
"sienna2",
"sienna3",
"sienna4",
"sky blue",
"SkyBlue",
"SkyBlue1",
"SkyBlue2",
"SkyBlue3",
"SkyBlue4",
"slate blue",
"slate gray",
"slate grey",
"SlateBlue",
"SlateBlue1",
"SlateBlue2",
"SlateBlue3",
"SlateBlue4",
"SlateGray",
"SlateGray1",
"SlateGray2",
"SlateGray3",
"SlateGray4",
"SlateGrey",
"snow",
"snow1",
"snow2",
"snow3",
"snow4",
"spring green",
"SpringGreen",
"SpringGreen1",
"SpringGreen2",
"SpringGreen3",
"SpringGreen4",
"steel blue",
"SteelBlue",
"SteelBlue1",
"SteelBlue2",
"SteelBlue3",
"SteelBlue4",
"tan",
"tan1",
"tan2",
"tan3",
"tan4",
"thistle",
"thistle1",
"thistle2",
"thistle3",
"thistle4",
"tomato",
"tomato1",
"tomato2",
"tomato3",
"tomato4",
"turquoise",
"turquoise1",
"turquoise2",
"turquoise3",
"turquoise4",
"violet",
"violet red",
"VioletRed",
"VioletRed1",
"VioletRed2",
"VioletRed3",
"VioletRed4",
"wheat",
"wheat1",
"wheat2",
"wheat3",
"wheat4",
"white",
"white smoke",
"WhiteSmoke",
"yellow",
"yellow green",
"yellow1",
"yellow2",
"yellow3",
"yellow4",
"YellowGreen"
]

class Trace(object):

    def __init__(self, tag, name, width=None):
        self.tag = tag
        self.name = name
        self.width = width
        self.vcd_name = name
        self.vp_name = '/' + name.replace('.', '/')
        if width is not None:
            self.vcd_name = self.vcd_name + width

    def get_vcd(self):
        return self.vcd_name

    def get_vp(self):
        return self.vp_name


class Trace_pool(object):

    def __init__(self):
        self.traces = []

    def get(self, tag, name, width=None):
        trace = Trace(tag, name, width)
        self.traces.append(trace)
        return trace.get_vcd()

    def get_traces(self, tags=None):
        if tags is None:
            return self.traces
        else:
            result = []
            for trace in self.traces:
                if trace.tag is None or trace.tag in tags:
                    result.append(trace)
            return result


def gen_gtkw_core_traces(gtkw, tp, path):
    gtkw.trace(tp.get('pc', path + '.pc', '[31:0]'), 'pc')
    gtkw.trace(tp.get('asm', path + '.asm'), 'asm')
    gtkw.trace(tp.get('debug', path + '.func'), 'func')
    gtkw.trace(tp.get('debug', path + '.inline_func'), 'inline_func')
    gtkw.trace(tp.get('debug', path + '.file'), 'file')
    gtkw.trace(tp.get('debug', path + '.line', '[31:0]'), 'line', datafmt='dec')
    with gtkw.group('events', closed=True):
        gtkw.trace(tp.get('core_events', path + '.pcer_cycles'), 'cycles')
        gtkw.trace(tp.get('core_events', path + '.pcer_instr'), 'instr')
        gtkw.trace(tp.get('core_events', path + '.pcer_ld_stall'), 'ld_stall')
        gtkw.trace(tp.get('core_events', path + '.pcer_jmp_stall'), 'jmp_stall')
        gtkw.trace(tp.get('core_events', path + '.pcer_imiss'), 'imiss')
        gtkw.trace(tp.get('core_events', path + '.pcer_ld'), 'ld')
        gtkw.trace(tp.get('core_events', path + '.pcer_st'), 'st')
        gtkw.trace(tp.get('core_events', path + '.pcer_jump'), 'jump')
        gtkw.trace(tp.get('core_events', path + '.pcer_branch'), 'branch')
        gtkw.trace(tp.get('core_events', path + '.pcer_taken_branch'), 'taken_branch')
        gtkw.trace(tp.get('core_events', path + '.pcer_rvc'), 'rvc')
        gtkw.trace(tp.get('core_events', path + '.pcer_ld_ext'), 'ld_ext')
        gtkw.trace(tp.get('core_events', path + '.pcer_st_ext'), 'st_ext')
        gtkw.trace(tp.get('core_events', path + '.pcer_ld_ext_cycles'), 'ld_ext_cycles')
        gtkw.trace(tp.get('core_events', path + '.pcer_st_ext_cycles'), 'st_ext_cycles')
        gtkw.trace(tp.get('core_events', path + '.pcer_tcdm_cont'), 'tcdm_cont')
        gtkw.trace(tp.get('core_events', path + '.misaligned'), 'misaligned')


def gen_gtkw_icache_traces(gtkw, tp, path, nb_ways, nb_sets):
    gtkw.trace(tp.get('refill', path + '.refill', '[31:0]'), 'refill')
    gtkw.trace(tp.get('input', path + '.port_0', '[31:0]'), 'input')
    for way in range(0, nb_ways):
        with gtkw.group('way_%d' % way, closed=True):
            for line in range(0, nb_sets):
                name = 'tag_%d' % line
                gtkw.trace(tp.get(name, path + '.set_%d.line_%d' % (way, line), '[31:0]'), name)



def check_user_traces(gtkw, tp, path, user_traces):
    if user_traces is not None:
        traces = user_traces.get_items()
        if traces is not None:
            for name, trace in user_traces.get_items().items():
                view_path = trace.get_str('view_path')

                if view_path.find('.') == -1:
                    parent = None
                    name = view_path
                else:
                    parent, name = view_path.rsplit('.', 1)

                if parent == path:
                    tag = trace.get_str('tag')
                    vcd_path = trace.get_str('vcd_path')
                    trace_filter = trace.get_str('filter')
                    if trace_filter is not None:
                        trace_filter = os.path.join(os.getcwd(), trace_filter)

                    width = None
                    if vcd_path.find('[') != -1:
                        vcd_path, width = vcd_path.split('[')
                        width = '[' + width

                    gtkw.trace(tp.get(tag, vcd_path, width), view_path, datafmt='dec', translate_filter_file=trace_filter)


def gen_gtkw_vector(gtkw, path, name, traces=[], trace_filter=None):
    vector_traces = []

    for trace in traces:
        for i in range(0, 8):
            vector_traces.append('(%d)%s' % (i, trace[0]))

    vector_filer = os.path.join(os.getcwd(), '%s.%s.txt' % (path, name))

    with open(vector_filer, 'w') as file:
        for i in range(0, len(traces)+1):
            file.write('%2d ?CadetBlue?ACTIVE\n' % i)

    with gtkw.vector(name, traces=vector_traces, extraflags=['popcnt', 'closed'], color='green', datafmt='dec', translate_filter_file=vector_filer):

        for trace in traces:
            gtkw.trace(trace[0], trace[1], translate_filter_file=trace_filter)


def gen_rt_traces_for_cluster(config, gv_config, cluster, cluster_alias):
    nb_pe = config.get_int('**/%s/nb_pe' % cluster)
    for i in range(0, nb_pe):
        pe_conf = {
            'tag': 'overview',
            'type': 'int',
            'path': '/user/runtime/%s/pe%d' % (cluster_alias, i),
            'vcd_path': 'user.runtime.%s.pe%d[31:0]' % (cluster_alias, i),
            'view_path': 'overview.%s.runtime.pe%d' % (cluster, i),
            'filter': 'rt_state.txt'
        }

        gv_config.set('events/include_regex/%s_pe%d' % (cluster, i), pe_conf)



def gen_rt_traces(config, gv_config):
    nb_cluster = config.get_int('**/nb_cluster')

    if nb_cluster is not None:
        for cid in range(0, nb_cluster):
            gen_rt_traces_for_cluster(config, gv_config, 'cluster' if cid == 0 else 'cluster_%d' % cid, 'cluster_%d' % cid)



def gen_gtkw_files(config, gv_config, chip_path='sys.board.'):
    nb_pe = config.get_int('**/cluster/nb_pe')

    user_traces = gv_config.get('**/events/traces')
    tags = gv_config.get('**/events/tags').get_dict()

    gen_rt_traces(config, gv_config)

    # Remove trace file so that we can switch between regular file and fifo
    if os.path.exists('all.vcd'):
        os.remove('all.vcd')

    core_state_file = os.path.join(os.getcwd(), 'core_state.txt')
    rt_state_file = os.path.join(os.getcwd(), 'rt_state.txt')
    all_state_file = os.path.join(os.getcwd(), 'all_state.txt')

    with open(core_state_file, 'w') as file:
        file.write('01 ?CadetBlue?ACTIVE\n')

    with open(all_state_file, 'w') as file:
        for i in range(0, len(gtkw_colors)):
            file.write('%d ?%s?ACTIVE\n' % (i, gtkw_colors[i]))

    with open(rt_state_file, 'w') as file:
        file.write('0 ?DarkSlateGray3?ENTRY\n')
        file.write('1 ?CadetBlue?FORK\n')
        file.write('2 ?DarkSlateGrey?BARRIER\n')
        file.write('3 ?DarkSlateGrey?CRITICAL\n')
        file.write('4 ?DarkSlateGrey?DMA_PUSH\n')
        file.write('5 ?DarkSlateGrey?DMA_WAIT\n')

    tp = Trace_pool()

    if len(gv_config.get('events/include_regex').get()) != 0 or gv_config.get_bool('events/enabled'):
        path = os.path.join(os.getcwd(), 'view.gtkw')
        with open(path, 'w') as file:
            gtkw = gtkw_new.GTKWSave(file)

            gtkw.dumpfile('all.vcd')

            with gtkw.group('overview'):
                check_user_traces(gtkw, tp, 'overview', user_traces)
                with gtkw.group('soc'):
                    check_user_traces(gtkw, tp, 'overview.soc', user_traces)
                    gtkw.trace(tp.get('overview', chip_path + 'chip.soc.fc.state', '[7:0]'), 'fc', translate_filter_file=core_state_file)

                    gen_gtkw_vector(gtkw, chip_path + 'chip.soc', 'udma', trace_filter=core_state_file, traces=[
                        [tp.get('overview', chip_path + 'chip.soc.udma.spim0_rx.state', '[7:0]'), 'spim0_rx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.spim0_tx.state', '[7:0]'), 'spim0_tx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.spim1_rx.state', '[7:0]'), 'spim1_rx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.spim1_tx.state', '[7:0]'), 'spim1_tx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.hyper0_rx.state', '[7:0]'),'hyper0_rx' ],
                        [tp.get('overview', chip_path + 'chip.soc.udma.hyper0_tx.state', '[7:0]'), 'hyper0_tx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2c0_rx.state', '[7:0]'), 'ic20_rx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2c0_tx.state', '[7:0]'), 'ic20_tx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2c1_rx.state', '[7:0]'), 'ic21_rx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2c1_tx.state', '[7:0]'), 'i2c1_tx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2s0_rx.state', '[7:0]'), 'i2s0_rx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2s0_tdm_0.state', '[7:0]'), 'i2s0_tdm_0'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2s0_tdm_1.state', '[7:0]'), 'i2s0_tdm_1'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2s0_tdm_2.state', '[7:0]'), 'i2s0_tdm_2'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2s0_tdm_3.state', '[7:0]'), 'i2s0_tdm_3'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2s0_tdm_4.state', '[7:0]'), 'i2s0_tdm_4'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2s0_tdm_5.state', '[7:0]'), 'i2s0_tdm_5'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2s0_tdm_6.state', '[7:0]'), 'i2s0_tdm_6'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.i2s0_tdm_7.state', '[7:0]'), 'i2s0_tdm_7'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.uart0_rx.state', '[7:0]'), 'uart0_rx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.uart0_tx.state', '[7:0]'), 'uart0_tx'],
                        [tp.get('overview', chip_path + 'chip.soc.udma.cpi0_rx.state', '[7:0]'), 'cpi0_rx']
                    ])

                    gtkw.trace(tp.get('overview', chip_path + 'chip.soc_clock.period'), 'period')
                    gtkw.trace(tp.get('clock', chip_path + 'chip.soc_clock.cycles'), 'cycles')

                if nb_pe is not None:
                    with gtkw.group('cluster'):
                        check_user_traces(gtkw, tp, 'overview.cluster', user_traces)
                        for i in range(0, nb_pe):
                            gtkw.trace(tp.get('overview', chip_path + 'chip.cluster.pe%d.state' % i, '[7:0]'), 'pe_%d' % i, translate_filter_file=core_state_file)

                        gen_gtkw_vector(gtkw, chip_path + 'chip.cluster', 'dma', trace_filter=core_state_file, traces=[
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_0', '[7:0]'), 'channel_0'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_1', '[7:0]'), 'channel_1'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_2', '[7:0]'), 'channel_2'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_3', '[7:0]'), 'channel_3'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_4', '[7:0]'), 'channel_4'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_5', '[7:0]'), 'channel_5'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_6', '[7:0]'), 'channel_6'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_7', '[7:0]'), 'channel_7'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_8', '[7:0]'), 'channel_8'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_9', '[7:0]'), 'channel_9'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_10', '[7:0]'), 'channel_10'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_11', '[7:0]'), 'channel_11'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_12', '[7:0]'), 'channel_12'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_13', '[7:0]'), 'channel_13'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_14', '[7:0]'), 'channel_14'],
                            [tp.get('overview', chip_path + 'chip.cluster.dma.channel_15', '[7:0]'), 'channel_15'],
                        ])

                        gtkw.trace(tp.get('overview', chip_path + 'chip.cluster.hwce.busy'), 'hwce')

                        gtkw.trace(tp.get('overview', chip_path + 'chip.cluster_clock.period'), 'period')
                        gtkw.trace(tp.get('clock', chip_path + 'chip.cluster_clock.cycles'), 'cycles')

                        with gtkw.group('runtime', closed=True):
                            check_user_traces(gtkw, tp, 'overview.cluster.runtime', user_traces)

                        with gtkw.group('stats', closed=True):
                            check_user_traces(gtkw, tp, 'overview.cluster.stats', user_traces)
                            for i in range(0, nb_pe):
                                gtkw.trace(tp.get('overview', chip_path + 'chip.cluster.pe%d.ipc_stat' % i), 'pe%d_ipc' % i, extraflags=['analog_step', 'analog_fullscale'])

            with gtkw.group('chip', closed=True):
                check_user_traces(gtkw, tp, 'chip', user_traces)
                with gtkw.group('fc', closed=True):
                    check_user_traces(gtkw, tp, 'chip.fc', user_traces)
                    gen_gtkw_core_traces(gtkw, tp, chip_path + 'chip.soc.fc')

                if config.get('**/fc_icache') is not None:
                    with gtkw.group('fc_icache', closed=True):
                        check_user_traces(gtkw, tp, 'chip.fc_icache', user_traces)
                        gen_gtkw_icache_traces(gtkw, tp, chip_path + 'chip.soc.fc_icache', 1<<config.get_int('**/fc_icache/nb_ways_bits'), 1<<config.get_int('**/fc_icache/nb_sets_bits'))


                if nb_pe is not None:
                    with gtkw.group('cluster', closed=True):
                        gtkw.trace(chip_path + 'chip.cluster.power_trace', datafmt='real', extraflags=['analog_step', 'analog_fullscale'])
                        check_user_traces(gtkw, tp, 'chip.cluster', user_traces)
                        for i in range(0, nb_pe):
                            with gtkw.group('pe_%d' % i, closed=True):
                                gen_gtkw_core_traces(gtkw, tp, chip_path + 'chip.cluster.pe%d' % i)

                        with gtkw.group('icache', closed=True):
                            check_user_traces(gtkw, tp, 'chip.cluster.icache', user_traces)
                            if config.get('**/cluster/icache/nb_ways_bits') is not None:
                                gen_gtkw_icache_traces(gtkw, tp, chip_path + 'chip.cluster.icache', 1<<config.get_int('**/cluster/icache/nb_ways_bits'), 1<<config.get_int('**/cluster/icache/nb_sets_bits'))

                        with gtkw.group('hwce', closed=True):
                            gtkw.trace(tp.get('hwce', chip_path + 'chip.cluster.hwce.conv_exec'), 'conv_exec')
                            gtkw.trace(tp.get('hwce', chip_path + 'chip.cluster.hwce.conv_value', '[31:0]'), 'conv_out')

        print ()
        print ('A Gtkwave script has been generated and can be opened with the following command:')
        print ('gtkwave ' + path)
        print ()

        for trace in tp.get_traces(tags):
            gv_config.set('events/include_regex', trace.get_vp())


    if gv_config.get_bool('**/events/gtkw'):
        gv_config.set('events/format', 'vcd')
        os.mkfifo('all.vcd')
        gtkw_new.spawn_gtkwave_interactive('all.vcd', 'view.gtkw', quiet=False)

