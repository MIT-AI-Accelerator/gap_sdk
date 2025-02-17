#
# Copyright (C) 2020 GreenWaves Technologies
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

from generators.v1.comp_gen import *
import generators.v1.soc_gen as soc_gen
import math
import collections

class Soc(object):
    
    def __init__(self, tp):
        chip              = tp.get_child_str('chip')
        has_cluster       = tp.get('cluster') is not None
        nb_cluster        = tp.get_child_int('cluster/nb_cluster')
        nb_pe             = tp.get_child_int('cluster/nb_pe')
        has_fc            = tp.get('soc/fc') is not None
        has_fc_eu         = tp.get('soc/fc_ico/peripherals/fc_eu') is not None
        has_fc_tcdm       = tp.get('soc/fc_ico/peripherals/fc_tcdm') is not None
        has_ddr           = tp.get('soc/ddr') is not None
        has_rtc           = tp.get('soc/peripherals/rtc') is not None or tp.get('soc/rtc') is not None
        rtc_version       = tp.get_child_int('soc/rtc/version')
        has_udma          = tp.get('soc/peripherals/udma') is not None
        udma_conf         = None
        if has_udma:
          udma_conf = js.import_config_from_file(tp.get_child_str('soc/peripherals/udma/content'), find=True, interpret=True)
        has_spi_master    = tp.get('soc/peripherals/spi_master') is not None
        has_uart          = tp.get('soc/peripherals/uart') is not None
        has_gpio          = tp.get('soc/peripherals/gpio') is not None
        has_soc_events    = tp.get('soc/peripherals/soc_eu') is not None
        if has_fc_eu:
          fc_events         = tp.get('soc/fc_ico/peripherals/fc_eu/irq')
        else:
          fc_events         = tp.get('soc/peripherals/fc_itc/irq')
        l2_is_partitioned = tp.get_child_bool('soc/l2/is_partitioned')
        has_fll           = tp.get('soc/peripherals/fll') is not None or tp.get('soc/peripherals/flls') is not None
        has_rom           = tp.get('soc/rom') is not None
        has_mram          = tp.get('soc/mram') is not None
        has_efuse         = tp.get('soc/peripherals/efuse') is not None
        has_pmu           = tp.get('soc/peripherals/pmu') is not None
        has_fc_icache     = tp.get('**/peripherals/fc_icache') is not None
        taps_conf         = tp.get('soc/taps')
        has_fast_clock    = tp.get_child_bool('has_fast_clock')
    
        comps = {}
    
        if fc_events is not None:
          fc_events_dict = fc_events.get_dict()
        else:
          fc_events_dict = OrderedDict()
    
    
        fc_itc_name = 'fc_eu' if has_fc_eu else 'fc_itc'
    
    
        if has_soc_events:
          soc_events_ids = tp.get('soc_events').get_dict()
        else:
          soc_events_ids = OrderedDict()
    
        def get_cluster_name(cid):
          if cid == 0:
            return 'cluster'
          else:
            return 'cluster_%d' % (cid)
    
        soc = Component(properties=OrderedDict([
            ('nb_cluster', nb_cluster),
            ('vp_class', "pulp/soc"),
            ('vp_component', 'utils.composite_impl'),
            ('peripherals_base',  tp.get_child_str("soc/peripherals/base")),
            ('soc_events_ids', soc_events_ids),
            ('fc_events', fc_events_dict)
        ]))
    
        axi_ico_mappings = OrderedDict([
          ("soc", get_mapping(tp.get_child_dict("soc")))
        ])
    
        if has_cluster:
          for cid in range(0, nb_cluster):
            cluster_name = get_cluster_name(cid)
            base = tp.get_child_int("cluster/base")
            size = tp.get_child_int("cluster/size")
            axi_ico_mappings[cluster_name] = OrderedDict([
              ("base", "0x%x" % (base + size * cid)),
              ("size", "0x%x" % (size))
            ])
    
        if has_ddr:
          axi_ico_mappings["ddr"] = get_mapping(tp.get_child_dict('soc/ddr'), True)
    
        soc.axi_ico = Component(properties=OrderedDict([
            ('@includes@', ["ips/interco/router.json"]),
            ('latency', 9),
            ('mappings', axi_ico_mappings)
        ]))
    
    
        soc.soc_ico = Component(properties=OrderedDict([
            ('nb_l2_shared_banks', tp.get_child_int("soc/l2/shared/nb_banks")),
            ('gv_class', "pulp.Soc_Ico_v2.Soc_Ico"),
            ('vp_class', None),
            ('vp_component', "")
        ]))
    
        ll_ico_mappings = OrderedDict(OrderedDict([
          ("apb", get_mapping(tp.get_child_dict("soc/peripherals")))
        ]))
    
        if has_rom:
          ll_ico_mappings.update(OrderedDict([
            ("rom", get_mapping(tp.get_child_dict("soc/rom")))
          ]))
    
        if has_cluster:
          ll_ico_mappings.update(OrderedDict([
            ("axi_master", OrderedDict([
              ("base", tp.get_child_str("cluster/base")),
              ("size", "0x%x" % (tp.get_child_int("cluster/size") * nb_cluster))
            ]))
          ]))
    
        if l2_is_partitioned:
          ll_ico_mappings.update(OrderedDict([
            ("l2_priv0", get_mapping(tp.get_child_dict("soc/l2/priv0"), True)),
            ("l2_priv0_alias", get_mapping(tp.get_child_dict("soc/l2/priv0_alias"))),
            ("l2_priv1", get_mapping(tp.get_child_dict("soc/l2/priv1"), True)),
            ("l2_shared", get_mapping(tp.get_child_dict("soc/l2/shared"))),
          ]))
        else:
          mapping = get_mapping(tp.get_child_dict("soc/l2"), True)
          ll_ico_mappings.update({
            "l2"         : mapping,
          })
    
        soc.soc_ico.ll_ico = Component(properties=OrderedDict([
          ('@includes@', [ "ips/interco/router.json" ]),
          ('mappings', ll_ico_mappings)
        ]))
    
        soc.soc_ico.hb_ico = Component(properties=OrderedDict([
          ('@includes@', ["ips/interco/router.json"]),
          ('remove_offset', tp.get_child_str("soc/l2/shared/base")),
          ('mappings', OrderedDict([]))
        ]))

        if has_fc:
    
          latency = 5
    
          soc.soc_ico.fc_fetch_ico = Component(properties=OrderedDict([
            ('@includes@', [ "ips/interco/router.json" ]),
            ('latency', latency),
            ('mappings', OrderedDict([
              ("l2_shared", get_mapping(tp.get_child_dict("soc/l2/shared"))),
              ("ll_ico", OrderedDict())
            ]))
          ]))
    
          soc.soc_ico.fc_data_ico = Component(properties=OrderedDict([
            ('@includes@', [ "ips/interco/router.json" ]),
            ('mappings', OrderedDict([
              ("l2_shared", get_mapping(tp.get_child_dict("soc/l2/shared"))),
              ("ll_ico", OrderedDict())
            ]))
          ]))
    
        if has_udma:
          soc.soc_ico.udma_rx_ico = Component(properties=OrderedDict([
            ('@includes@', [ "ips/interco/router.json" ]),
            ('mappings', OrderedDict([
              ("l2_shared", get_mapping(tp.get_child_dict("soc/l2/shared"))),
              ("ll_ico", OrderedDict())
            ]))
          ]))
    
          soc.soc_ico.udma_tx_ico = Component(properties=OrderedDict([
            ('@includes@', [ "ips/interco/router.json" ]),
            ('mappings', OrderedDict([
              ("l2_shared", get_mapping(tp.get_child_dict("soc/l2/shared"))),
              ("ll_ico", OrderedDict())
            ]))
          ]))
    
        soc.soc_ico.debug                  = soc.soc_ico.ll_ico.input
        soc.soc_ico.axi_slave              = soc.soc_ico.ll_ico.input
    
        l2_shared_size = tp.get_child_int("soc/l2/shared/size")
        l2_shared_nb_regions = tp.get_child_int("soc/l2/shared/nb_regions")
        region_base = tp.get_child_int("soc/l2/shared/base")
        region_size = int(l2_shared_size / l2_shared_nb_regions)

        for i in range(0, tp.get_child_int("soc/l2/shared/nb_regions")):

          soc.soc_ico.hb_ico.get_property('mappings')['l2_shared_%d' % i] = OrderedDict([("base", region_base), ("size", "0x%x" % region_size), ('remove_offset', region_base)])
          soc.soc_ico.hb_ico.set('l2_shared_%d' % i, soc.soc_ico.new_itf('l2_shared_%d' % i))
          region_base += region_size
            
        if has_fc:
          soc.soc_ico.fc_fetch               = soc.soc_ico.fc_fetch_ico.input
          soc.soc_ico.fc_data                = soc.soc_ico.fc_data_ico.input
          soc.soc_ico.fc_fetch_ico.l2_shared = soc.soc_ico.hb_ico.input
          soc.soc_ico.fc_fetch_ico.ll_ico    = soc.soc_ico.ll_ico.input
          soc.soc_ico.fc_data_ico.l2_shared  = soc.soc_ico.hb_ico.input
          soc.soc_ico.fc_data_ico.ll_ico     = soc.soc_ico.ll_ico.input
    
        if has_udma:
          soc.soc_ico.udma_tx                = soc.soc_ico.udma_tx_ico.input
          soc.soc_ico.udma_rx_ico.l2_shared  = soc.soc_ico.hb_ico.input
          soc.soc_ico.udma_rx_ico.ll_ico     = soc.soc_ico.ll_ico.input
          soc.soc_ico.udma_tx_ico.l2_shared  = soc.soc_ico.hb_ico.input
          soc.soc_ico.udma_tx_ico.ll_ico     = soc.soc_ico.ll_ico.input
        soc.soc_ico.ll_ico.apb             = soc.soc_ico.apb
        if has_rom:
          soc.soc_ico.ll_ico.rom             = soc.soc_ico.apb
    
        if l2_is_partitioned:
          soc.soc_ico.ll_ico.l2_priv0        = soc.soc_ico.l2_priv0
          soc.soc_ico.ll_ico.l2_priv0_alias  = soc.soc_ico.l2_priv0
          soc.soc_ico.ll_ico.l2_priv1        = soc.soc_ico.l2_priv1
          soc.soc_ico.ll_ico.l2_shared       = soc.soc_ico.hb_ico.input
        else:
          soc.soc_ico.ll_ico.l2            = soc.soc_ico.l2
    
        if has_cluster:
          soc.soc_ico.ll_ico.axi_master      = soc.soc_ico.axi_master
    
    
    
    
    
        apb_soc_mappings = OrderedDict([
          ("stdout", get_mapping(tp.get_child_dict("soc/peripherals/stdout"), True)),
          ("apb_soc_ctrl", get_mapping(tp.get_child_dict("soc/peripherals/apb_soc_ctrl"), True)),
        ])
    
        if has_soc_events:
          apb_soc_mappings.update({
            "soc_eu"       : get_mapping(tp.get_child_dict("soc/peripherals/soc_eu"), True),
          })
    
        if has_gpio:
          apb_soc_mappings.update({
            "gpio"         : get_mapping(tp.get_child_dict("soc/peripherals/gpio"), True)
          })
    
        if has_fll:
    
          flls_config = tp.get('soc/peripherals/flls')
    
          if flls_config is None:
            apb_soc_mappings.update(OrderedDict([
              ("fll", get_mapping(tp.get_child_dict("soc/peripherals/fll"), True)),
              ("fll1", get_mapping(tp.get_child_dict("soc/peripherals/fll1"), True)),
              ("fll2", get_mapping(tp.get_child_dict("soc/peripherals/fll2"), True))
            ]))
          else:
            for fll_name, fll_config in flls_config.get_items().items():
              apb_soc_mappings.update({
                fll_name          : get_mapping(fll_config.get_dict(), True)
              })
    
        if has_udma:
          apb_soc_mappings.update({
            "udma"         : get_mapping(tp.get_child_dict("soc/peripherals/udma"), True),
          })
    
        if has_fc_icache:
            apb_soc_mappings.update({
              "fc_icache"       : get_mapping(tp.get_child_dict("**/peripherals/fc_icache"), True)
            })
    
        if has_fc:
            apb_soc_mappings.update({
              "fc_itc"       : get_mapping(tp.get_child_dict("soc/peripherals/%s" % fc_itc_name), True)
            })
            apb_soc_mappings.update(OrderedDict([
              ("fc_debug", get_mapping(tp.get_child_dict("soc/peripherals/fc_dbg_unit"), True)),
              ("fc_dbg_unit", get_mapping(tp.get_child_dict("soc/peripherals/fc_dbg_unit"), True)),
            ]))
    
    
        if has_efuse:
          apb_soc_mappings.update({
            "efuse"           : get_mapping(tp.get_child_dict("soc/peripherals/efuse"), True)
          })
    
        if has_pmu:
          apb_soc_mappings.update({
            "pmu"       : get_mapping(tp.get_child_dict("soc/peripherals/pmu"), True),
          })
    
        if has_rom:
          apb_soc_mappings.update({
            "rom"       : get_mapping(tp.get_child_dict("soc/rom"), True),
          })
    
        if tp.get_child_dict("soc/peripherals/rtc") is not None:
          apb_soc_mappings.update({
            "rtc"       : get_mapping(tp.get_child_dict("soc/peripherals/rtc"), True),
          })
          
    
        soc.apb_ico = Component(properties=OrderedDict([
            ('@includes@', [ "ips/interco/router.json" ]),
            ('latency', 8),
            ('mappings', apb_soc_mappings)
        ]))
    

        soc.fc_ico = Component(properties=OrderedDict([
            ('l2_alias', True)
        ]))
    
    
        core_config_dict = tp.get('soc/fc/core_config').get_dict()
        core_config_dict.update(OrderedDict([
              ('cluster_id', tp.get_child_int("soc/fc/cluster_id")),
              ('core_id', tp.get_child_int("soc/fc/core_id")),
              ('fetch_enable', tp.get_child_bool("soc/fc/fetch_enable")),
              ('boot_addr', tp.get_child_str("soc/fc/boot_addr"))
        ]))

        soc.fc = Component(properties=core_config_dict)
    
        apb_soc_params = OrderedDict([
          ('@includes@', ["chips/%s/apb_soc.json" % chip])
        ])
    
        if has_cluster and has_pmu:
          apb_soc_params['cluster_power_event'] = tp.get_child_int('soc_events/soc_evt_cluster_pok')
          apb_soc_params['cluster_clock_gate_event'] = tp.get_child_int('soc_events/soc_evt_cluster_cg_ok')
    
        apb_soc_ctrl_config = tp.get('**/apb_soc_ctrl/config')
        if apb_soc_ctrl_config is not None:
          apb_soc_params.update(apb_soc_ctrl_config.get_dict())
        soc.apb_soc_ctrl = Component(properties=apb_soc_params)
    
        if l2_is_partitioned:
    
          soc.l2 = Component(properties=OrderedDict([
              ('is_partitioned', True),
              ('nb_shared_banks', tp.get_child_int("soc/l2/shared/nb_banks")),
              ('map_base', tp.get_child_str("soc/l2/base")),
              ('map_size', tp.get_child_str("soc/l2/size")),
              ('size', tp.get_child_str("soc/l2/size"))
          ]))
    
          soc.l2_priv0 = Component(properties=OrderedDict([
              ('size', tp.get_child_int("soc/l2/priv0/size")),
              ('map_base', tp.get_child_str("soc/l2/priv0/base")),
              ('map_size', tp.get_child_str("soc/l2/priv0/size")),
              ('vp_class', "memory/memory"),
              ('vp_component', 'memory.memory_impl'),
          ]))
    
          soc.l2_priv1 = Component(properties=OrderedDict([
              ('size', tp.get_child_int("soc/l2/priv1/size")),
              ('map_base', tp.get_child_str("soc/l2/priv1/base")),
              ('map_size', tp.get_child_str("soc/l2/priv1/size")),
              ('vp_class', "memory/memory"),
              ('vp_component', 'memory.memory_impl'),
          ]))
    
          soc.l2_shared = Component(properties=OrderedDict([
              ('nb_banks', tp.get_child_int("soc/l2/shared/nb_banks")),
              ('size', tp.get_child_int("soc/l2/shared/size")),
              ('map_base', tp.get_child_str("soc/l2/shared/base")),
              ('map_size', tp.get_child_str("soc/l2/shared/size")),
              ('mappings', OrderedDict([]))
          ]))
    
          l2_shared_size = tp.get_child_int("soc/l2/shared/size")
          l2_shared_nb_banks = tp.get_child_int("soc/l2/shared/nb_banks")
          l2_shared_nb_regions = tp.get_child_int("soc/l2/shared/nb_regions")

          cut_size = int(l2_shared_size / l2_shared_nb_regions / l2_shared_nb_banks)

          for i in range(0, l2_shared_nb_regions):

            interleaver = Component(properties=OrderedDict([
              ('@includes@', [ "ips/interco/interleaver.json" ]),
              ('nb_slaves', tp.get_child_int("soc/l2/shared/nb_banks")),
              ('interleaving_bits', tp.get_child_int("soc/l2/shared/interleaving_bits"))
            ]))

            soc.add_component('l2_shared_%d' % i, interleaver)

            soc.soc_ico.set('l2_shared_%d' % i, interleaver.input)

            for j in range(0, l2_shared_nb_banks):

              cut = Component(properties=OrderedDict([
                  ('size', cut_size),
                  ('vp_class', "memory/memory"),
                  ('vp_component', 'memory.memory_impl'),
              ]))

              soc.add_component('l2_shared_%d_cut_%d' % (i, j), cut)

              interleaver.set('out_%d' % j, cut.input)

              soc.apb_soc_ctrl.set('l2_power_ctrl_' + str(i), cut.power_ctrl)

        else:
    
          soc.l2 = Component(properties=OrderedDict([
              ('size', tp.get_child_int("soc/l2/size")),
              ('map_base', tp.get_child_str("soc/l2/base")),
              ('map_size', tp.get_child_str("soc/l2/size")),
              ('vp_class', "memory/memory"),
              ('vp_component', 'memory.memory_impl'),
          ]))
    
        if has_rom:
          rom_config_dict = collections.OrderedDict([
            ('@includes@', ["ips/rom/rom_v%d.json" % tp.get_child_int("soc/rom/version")]),
            ('size', tp.get_child_int("soc/rom/size")),
            ('map_base', tp.get_child_str("soc/rom/base")),
            ('map_size', tp.get_child_str("soc/rom/size")),
            ('vp_class', "memory/memory"),
            ('vp_component', 'memory.memory_impl'),
          ])
          rom_config = tp.get('soc/rom/config')
          if rom_config is not None:
            rom_config_dict.update(rom_config.get_dict())
    
          soc.rom = Component(properties=rom_config_dict)
    
        soc.plt_loader = Component(properties=OrderedDict([
            ('@includes@', ["tools/plt_loader/plt_loader.json"])
        ]))
    
        if has_fc:
            soc.fc_itc = Component(properties=OrderedDict([
                ('@includes@', ["ips/itc/itc_v%d.json" % (tp.get_child_int("soc/peripherals/%s/version" % fc_itc_name))])
            ]))
    
        if has_fll:
    
          flls_config = tp.get('soc/peripherals/flls')
    
          if flls_config is None:
            soc.fll = Component(properties=OrderedDict([
                ('@includes@', ["ips/fll/fll_v%d.json" % (tp.get_child_int("soc/peripherals/fll/version"))])
            ]))
    
            soc.fll1 = Component(properties=OrderedDict([
                ('@includes@', ["ips/fll/fll_v%d.json" % (tp.get_child_int("soc/peripherals/fll/version"))])
            ]))
    
            soc.fll2 = Component(properties=OrderedDict([
                ('@includes@', ["ips/fll/fll_v%d.json" % (tp.get_child_int("soc/peripherals/fll/version"))])
            ]))
    
            if has_fast_clock:
              soc.fast_clock = soc.fll.ref_clock
              soc.fast_clock = soc.fll1.ref_clock
              soc.fast_clock = soc.fll2.ref_clock
            else:
              soc.ref_clock = soc.fll.ref_clock
              soc.ref_clock = soc.fll1.ref_clock
              soc.ref_clock = soc.fll2.ref_clock
    
          else:
            for fll_name, fll_config in flls_config.get_items().items():
    
              soc.add_component(fll_name, Component(properties=OrderedDict([
                  ('@includes@', ["ips/fll/fll_v%d.json" % (fll_config.get_child_int("version"))])
              ])))
    
              if has_fast_clock:
                soc.fast_clock = soc.get(fll_name).ref_clock
              else:
                soc.ref_clock = soc.get(fll_name).ref_clock
    
    
          soc.fll_ctrl = Component(properties=OrderedDict([
              ('version', tp.get_child_int("soc/peripherals/fll_ctrl/version")),
              ('vp_class', "pulp/fll/fll_ctrl"),
              ('vp_component', "pulp.fll.fll_ctrl_impl"),
              ('gv_class', "pulp.Fll_ctrl.fll_ctrl")
          ]))
    
    
        soc.stdout = Component(properties=OrderedDict([
            ('@includes@', ["ips/stdout/stdout_v%d.json" % tp.get_child_int("soc/peripherals/stdout/version")])
        ]))
    
        if has_fc_tcdm:
          soc.fc_tcdm = Component(properties=OrderedDict([
              ('size', tp.get_child_int("soc/fc_ico/peripherals/fc_tcdm/size")),
              ('vp_class', "memory/memory"),
              ('vp_component', 'memory.memory_impl'),
          ]))
    
    
        if has_gpio:
          gpio_config = OrderedDict([
            ('@includes@', ["ips/gpio/gpio_v%d.json" % tp.get_child_int("soc/peripherals/gpio/version")])
          ])
          if tp.get('soc_events') is not None:
            gpio_config['soc_event'] = tp.get('soc_events').get_int('soc_evt_gpio')
    
          soc.gpio = Component(properties=gpio_config)
    
          soc.apb_ico.gpio = soc.gpio.input
    
          nb_gpio = tp.get_child_int("soc/peripherals/gpio/nb_gpio")
          if nb_gpio is None:
            nb_gpio = 32
    
          for i in range(0, nb_gpio):
            soc.set('gpio%d' % i, soc.gpio.new_itf('gpio%d' % i))
            if has_pmu and tp.get_int('soc/peripherals/pmu/version') < 3:
              soc.set('gpio%d' % i, soc.apb_soc_ctrl.new_itf('wakeup_gpio%d' % i))
    
          if has_pmu:
            if tp.get_int('soc/peripherals/pmu/version') == 3:
              soc.set('gpio64', soc.apb_soc_ctrl.new_itf('wakeup_gpio0'))
    
    
    
        for name, config in tp.get("soc/peripherals").get_items().items():
          file = config.get_child_str("file")
          if file is not None:
            apb_soc_mappings.update({
              name : get_mapping(config.get_dict(), True),
            })
            comp_config = OrderedDict([('@includes@', [ file ])])
            if config.get('config') is not None:
              comp_config.update(config.get('config').get_dict())
            soc.add_component(name, Component(properties=comp_config))
            soc.apb_ico.set(name, soc.get(name).input)
    
    
        if has_fc_icache:
          soc.fc_icache_ctrl = Component(properties=OrderedDict([
              ('@includes@', ["ips/icache_ctrl/icache_ctrl_v%d.json" % tp.get_child_int("**/fc_icache/version")])
          ]))
    
          icache_config_dict = OrderedDict([
            ('@includes@', ["ips/cache/cache.json"])
          ])
    
          icache_config = tp.get('**/fc_icache/config')
    
          if icache_config is not None:
            icache_config_dict.update(icache_config.get_dict())
    
          soc.fc_icache = Component(properties=icache_config_dict)
    
          soc.fc_icache_ctrl.enable = soc.fc_icache.enable
          soc.fc_icache_ctrl.flush = soc.fc_icache.flush
          soc.fc_icache_ctrl.flush = soc.fc.flush_cache
          soc.fc_icache_ctrl.flush_line = soc.fc_icache.flush_line
          soc.fc_icache_ctrl.flush_line_addr = soc.fc_icache.flush_line_addr
          soc.fc.flush_cache_req = soc.fc_icache.flush
          soc.fc_icache.flush_ack = soc.fc.flush_cache_ack
    

        #
        # Timers
        #
        soc.timer = Component(properties=OrderedDict([
            ('@includes@', ["ips/timer/timer_v%d.json" % tp.get_child_int("soc/peripherals/fc_timer/version")])
        ]))
        
        soc.timer_1 = Component(properties=OrderedDict([
            ('@includes@', ["ips/timer/timer_v%d.json" % tp.get_child_int("soc/peripherals/fc_timer_1/version")])
        ]))

        soc.apb_ico.get_property('mappings')["fc_timer"] = get_mapping(tp.get_child_dict("soc/peripherals/fc_timer"), True)
        soc.apb_ico.get_property('mappings')["fc_timer_1"] = get_mapping(tp.get_child_dict("soc/peripherals/fc_timer_1"), True)

        soc.apb_ico.fc_timer = soc.timer.input
        soc.apb_ico.fc_timer_1 = soc.timer_1.input

        soc.timer.irq_itf_0 = soc.fc_itc.in_event_10
        soc.timer.irq_itf_1 = soc.fc_itc.in_event_11
        soc.timer_1.irq_itf_0 = soc.fc_itc.in_event_12
        soc.timer_1.irq_itf_1 = soc.fc_itc.in_event_13

        soc.apb_soc_ctrl.ref_clock_muxed = soc.timer.ref_clock
        soc.apb_soc_ctrl.ref_clock_muxed = soc.timer_1.ref_clock





        if has_soc_events:
          soc.soc_eu = Component(properties=OrderedDict([
              ('@includes@', ["ips/soc_eu/soc_eu_v%d.json" % tp.get_child_int("soc/peripherals/soc_eu/version")]),
              ('ref_clock_event', tp.get('soc_events').get('soc_evt_ref_clock').get_int())
          ]))
    
        if has_udma:
          content = tp.get_child_str('soc/peripherals/udma/content')
          if content is not None:
            soc.udma = Component(properties=OrderedDict([
                ('@includes@', [ content ])
            ]))
          else:
            soc.udma = Component(properties=OrderedDict([
                ('@includes@', ["chips/%s/udma.json" % chip])
            ]))
    
          comps['udma'] = soc.udma
    
          if has_mram:      
            mram_config_dict = collections.OrderedDict([
              ('@includes@', ["ips/mram/mram.json"])
            ])
            mram_config = tp.get('soc/mram/config')
            if mram_config is not None:
              mram_config_dict.update(mram_config.get_dict())
    
            soc.mram = Component(properties=mram_config_dict)
    
            soc.udma.mram0 = soc.mram.input

          soc.udma.i2s0_clk_out = soc.udma.i2s1_clk_in
          soc.udma.i2s0_ws_out = soc.udma.i2s1_ws_in
          soc.udma.i2s0_clk_out = soc.udma.i2s2_clk_in
          soc.udma.i2s0_ws_out = soc.udma.i2s2_ws_in
    
          soc.udma.i2s0_pdm_out_0 = soc.udma.sfu_pdm_out_0
          soc.udma.i2s0_pdm_out_1 = soc.udma.sfu_pdm_out_1
          soc.udma.i2s1_pdm_out_0 = soc.udma.sfu_pdm_out_2
          soc.udma.i2s1_pdm_out_1 = soc.udma.sfu_pdm_out_3
          soc.udma.i2s2_pdm_out_0 = soc.udma.sfu_pdm_out_4
          soc.udma.i2s2_pdm_out_1 = soc.udma.sfu_pdm_out_5

          soc.udma.i2s0_pdm_in_0 = soc.udma.sfu_pdm_in_0
          soc.udma.i2s0_pdm_in_1 = soc.udma.sfu_pdm_in_1
          soc.udma.i2s0_pdm_in_2 = soc.udma.sfu_pdm_in_2
          soc.udma.i2s0_pdm_in_3 = soc.udma.sfu_pdm_in_3
          soc.udma.i2s1_pdm_in_0 = soc.udma.sfu_pdm_in_4
          soc.udma.i2s1_pdm_in_1 = soc.udma.sfu_pdm_in_5
          soc.udma.i2s1_pdm_in_2 = soc.udma.sfu_pdm_in_6
          soc.udma.i2s1_pdm_in_3 = soc.udma.sfu_pdm_in_7
          soc.udma.i2s2_pdm_in_0 = soc.udma.sfu_pdm_in_8
          soc.udma.i2s2_pdm_in_1 = soc.udma.sfu_pdm_in_9
          soc.udma.i2s2_pdm_in_2 = soc.udma.sfu_pdm_in_10
          soc.udma.i2s2_pdm_in_3 = soc.udma.sfu_pdm_in_11

          soc.udma.i2s0_ws_out = soc.udma.sfu_ws_in_0
          soc.udma.i2s1_ws_out = soc.udma.sfu_ws_in_1
          soc.udma.i2s2_ws_out = soc.udma.sfu_ws_in_2

          soc.udma.sfu_stream_in_ready_0 = soc.udma.stream_in_ready_0
          soc.udma.sfu_stream_in_ready_1 = soc.udma.stream_in_ready_1
          soc.udma.sfu_stream_in_ready_2 = soc.udma.stream_in_ready_2
          soc.udma.sfu_stream_in_ready_3 = soc.udma.stream_in_ready_3
          soc.udma.sfu_stream_in_ready_4 = soc.udma.stream_in_ready_4
          soc.udma.sfu_stream_in_ready_5 = soc.udma.stream_in_ready_5
          soc.udma.sfu_stream_in_ready_6 = soc.udma.stream_in_ready_6
          soc.udma.sfu_stream_in_ready_7 = soc.udma.stream_in_ready_7
          soc.udma.sfu_stream_in_ready_8 = soc.udma.stream_in_ready_8
          soc.udma.sfu_stream_in_ready_9 = soc.udma.stream_in_ready_9
          soc.udma.sfu_stream_in_ready_10 = soc.udma.stream_in_ready_10
          soc.udma.sfu_stream_in_ready_11 = soc.udma.stream_in_ready_11
          soc.udma.sfu_stream_in_ready_12 = soc.udma.stream_in_ready_12
          soc.udma.sfu_stream_in_ready_13 = soc.udma.stream_in_ready_13
          soc.udma.sfu_stream_in_ready_14 = soc.udma.stream_in_ready_14
          soc.udma.sfu_stream_in_ready_15 = soc.udma.stream_in_ready_15
          
          soc.udma.stream_in_data_0 = soc.udma.sfu_stream_in_data_0
          soc.udma.stream_in_data_1 = soc.udma.sfu_stream_in_data_1
          soc.udma.stream_in_data_2 = soc.udma.sfu_stream_in_data_2
          soc.udma.stream_in_data_3 = soc.udma.sfu_stream_in_data_3
          soc.udma.stream_in_data_4 = soc.udma.sfu_stream_in_data_4
          soc.udma.stream_in_data_5 = soc.udma.sfu_stream_in_data_5
          soc.udma.stream_in_data_6 = soc.udma.sfu_stream_in_data_6
          soc.udma.stream_in_data_7 = soc.udma.sfu_stream_in_data_7
          soc.udma.stream_in_data_8 = soc.udma.sfu_stream_in_data_8
          soc.udma.stream_in_data_9 = soc.udma.sfu_stream_in_data_9
          soc.udma.stream_in_data_10 = soc.udma.sfu_stream_in_data_10
          soc.udma.stream_in_data_11 = soc.udma.sfu_stream_in_data_11
          soc.udma.stream_in_data_12 = soc.udma.sfu_stream_in_data_12
          soc.udma.stream_in_data_13 = soc.udma.sfu_stream_in_data_13
          soc.udma.stream_in_data_14 = soc.udma.sfu_stream_in_data_14
          soc.udma.stream_in_data_15 = soc.udma.sfu_stream_in_data_15

          soc.udma.stream_out_ready_0 = soc.udma.sfu_stream_out_ready_0
          soc.udma.stream_out_ready_1 = soc.udma.sfu_stream_out_ready_1
          soc.udma.stream_out_ready_2 = soc.udma.sfu_stream_out_ready_2
          soc.udma.stream_out_ready_3 = soc.udma.sfu_stream_out_ready_3
          soc.udma.stream_out_ready_4 = soc.udma.sfu_stream_out_ready_4
          soc.udma.stream_out_ready_5 = soc.udma.sfu_stream_out_ready_5
          soc.udma.stream_out_ready_6 = soc.udma.sfu_stream_out_ready_6
          soc.udma.stream_out_ready_7 = soc.udma.sfu_stream_out_ready_7
          soc.udma.stream_out_ready_8 = soc.udma.sfu_stream_out_ready_8
          soc.udma.stream_out_ready_9 = soc.udma.sfu_stream_out_ready_9
          soc.udma.stream_out_ready_10 = soc.udma.sfu_stream_out_ready_10
          soc.udma.stream_out_ready_11 = soc.udma.sfu_stream_out_ready_11
          soc.udma.stream_out_ready_12 = soc.udma.sfu_stream_out_ready_12
          soc.udma.stream_out_ready_13 = soc.udma.sfu_stream_out_ready_13
          soc.udma.stream_out_ready_14 = soc.udma.sfu_stream_out_ready_14
          soc.udma.stream_out_ready_15 = soc.udma.sfu_stream_out_ready_15

          soc.udma.sfu_stream_out_data_0 = soc.udma.stream_out_data_0
          soc.udma.sfu_stream_out_data_1 = soc.udma.stream_out_data_1
          soc.udma.sfu_stream_out_data_2 = soc.udma.stream_out_data_2
          soc.udma.sfu_stream_out_data_3 = soc.udma.stream_out_data_3
          soc.udma.sfu_stream_out_data_4 = soc.udma.stream_out_data_4
          soc.udma.sfu_stream_out_data_5 = soc.udma.stream_out_data_5
          soc.udma.sfu_stream_out_data_6 = soc.udma.stream_out_data_6
          soc.udma.sfu_stream_out_data_7 = soc.udma.stream_out_data_7
          soc.udma.sfu_stream_out_data_8 = soc.udma.stream_out_data_8
          soc.udma.sfu_stream_out_data_9 = soc.udma.stream_out_data_9
          soc.udma.sfu_stream_out_data_10 = soc.udma.stream_out_data_10
          soc.udma.sfu_stream_out_data_11 = soc.udma.stream_out_data_11
          soc.udma.sfu_stream_out_data_12 = soc.udma.stream_out_data_12
          soc.udma.sfu_stream_out_data_13 = soc.udma.stream_out_data_13
          soc.udma.sfu_stream_out_data_14 = soc.udma.stream_out_data_14
          soc.udma.sfu_stream_out_data_15 = soc.udma.stream_out_data_15
    
        if has_spi_master:
          soc.spi_master = Component(properties=OrderedDict([
              ('@includes@', ["ips/spi_master/spi_master_v1.json"])
          ]))
    
        if has_uart:
          soc.apb_uart = Component(properties=OrderedDict([
              ('@includes@', ["ips/uart/uart_v0.json"])
          ]))
    
        if has_efuse:
          efuse_conf = tp.get('soc/peripherals/efuse')
          config = OrderedDict([
              ('@includes@', ["ips/efuse/efuse_v%d.json" % tp.get_child_int("soc/peripherals/efuse/version")])
          ])
          if efuse_conf.get('config') is not None:
            config.update(efuse_conf.get('config').get_dict())
          soc.efuse = Component(properties=config)
    
        soc.uart = Component(properties=OrderedDict([
            ('version', 1)
        ]))
    
        if has_gpio:
          if has_soc_events:
            soc.gpio.event = soc.soc_eu.event_in
          if has_fc:
            fc_irq = fc_events.get_child_int('evt_gpio')
            if fc_irq is not None:
              soc.gpio.irq = soc.fc_itc.new_itf('in_event_%d' % (fc_irq))
    
        if has_fc and tp.get_child_int("**/fc_dbg_unit/version") <= 1:
          soc.fc_debug = Component(properties=OrderedDict([
              ('version', tp.get_child_int("**/fc_dbg_unit/version"))
          ]))
    
        if has_cluster:
          for cid in range(0, nb_cluster):
            if tp.get_child_bool('**/apb_soc_ctrl/has_pmu_bypass'):
              soc.apb_soc_ctrl.cluster_reset = soc.cluster_reset
    
        if tp.get('**/gdbserver') is not None:
          gdbserver_config = OrderedDict([('@includes@', ["ips/gdbserver/gdbserver.json"])])
          if tp.get('**/gdbserver/config') is not None:
            gdbserver_config.update(tp.get('**/gdbserver/config').get_dict())
    
          soc.gdbserver = Component(properties=gdbserver_config)
    
        if taps_conf is None:
          adv_dbg_unit_config = OrderedDict([('@includes@', ["ips/adv_dbg_unit/adv_dbg_unit.json"])])
          if tp.get('**/adv_dbg_unit/config') is not None:
            adv_dbg_unit_config.update(tp.get('**/adv_dbg_unit/config').get_dict())
    
          soc.adv_dbg_unit = Component(properties=adv_dbg_unit_config)
        else:
    
          taps = []
    
          for tap_name in taps_conf.get_dict():
    
            tap_template = tp.get('soc').get(tap_name)
            tap_config = tap_template.get('config').get_dict()
    
            tap = Component(
              properties=tap_template.get('config').get_dict(),
              template=tap_template,
              config=tap_template.get('config')
            )
    
            soc.add_component(tap_name, tap)
    
            taps.append(tap)
    
            if tap_template.get_bool('riscv_debug'):
    
              debug_rom_config_dict = collections.OrderedDict([
                ('@includes@', ["ips/rom/rom_v%d.json" % tp.get_child_int("**/debug_rom/version")]),
                ('size', tp.get_child_int("**/debug_rom/size")),
                ('map_base', tp.get_child_str("**/debug_rom/base")),
                ('map_size', tp.get_child_str("**/debug_rom/size")),
                ('vp_class', "memory/memory"),
                ('vp_component', 'memory.memory_impl'),
              ])
              rom_config = tp.get('**/debug_rom/config')
              if rom_config is not None:
                debug_rom_config_dict.update(rom_config.get_dict())
    
              soc.debug_rom = Component(properties=debug_rom_config_dict)
    
              soc.apb_ico.get_property('mappings')['debug_rom'] = get_mapping(tp.get_child_dict("**/debug_rom"), True)
              soc.apb_ico.get_property('mappings')['debug_rom'] = get_mapping(tp.get_child_dict("**/debug_rom"), True)
    
              soc.apb_ico.debug_rom = soc.debug_rom.input
              soc.apb_ico.fc_dbg_unit = tap.input
    
              if chip == 'gap9_v2':
                for i in range(0, 10):
                  soc.apb_soc_ctrl.set('dm_hart_available_' + str(i), tap.new_itf('hart_available_' + str(i)))
    
    
              tap.set_property('harts', [])
    
              if has_fc:
                hart_id = (tp.get_int('soc/fc/cluster_id') << 5) | (tp.get_int('soc/fc/core_id'))
                tap.get_property('harts').append([hart_id, 'fc'])
                tap.fc = soc.fc.halt
    
              for cluster in range(0, nb_cluster):
                for pe in range(0, nb_pe):
                  hart_id = (cluster << 5) | pe
    
                  name = 'cluster%d_pe%d' % (cluster, pe)
                  tap.get_property('harts').append([hart_id, name])
        
                  tap.set(name, soc.new_itf('halt_' + name))
    
    
    
        #
        # APB SOC CTRL
        #
        #for i in range(0, tp.get_child_int("soc/peripherals/apb_soc_ctrl/config/nb_l2_shared_banks")):
        #    soc.apb_soc_ctrl.set('l2_power_ctrl_' + str(i), soc.get('l2_shared_%d' % i).power_ctrl)

    
        #
        # XIP
        #
        soc.xip = Component(properties=OrderedDict([
            ('@includes@', ["ips/xip/xip_v%d.json" % tp.get_child_int("soc/peripherals/xip/version")]),
            ('nb_refill_itfs', 2)
        ]))

        # APB connection
        soc.apb_ico.get_property('mappings')['xip'] = get_mapping(tp.get_child_dict("soc/peripherals/xip"), True)
        soc.apb_ico.xip = soc.xip.apb_input

        # FC connections
        soc.soc_ico.fc_fetch_ico.get_property('mappings')['xip'] = get_mapping(tp.get_child_dict("soc/l2/xip"))
        soc.soc_ico.fc_fetch_ico.xip = soc.soc_ico.fc_fetch_input
        soc.soc_ico.fc_fetch_input = soc.xip.fc_fetch_input
        soc.soc_ico.fc_data_ico.get_property('mappings')['xip'] = get_mapping(tp.get_child_dict("soc/l2/xip"))
        soc.soc_ico.fc_data_ico.xip = soc.soc_ico.fc_data_input
        soc.soc_ico.fc_data_input = soc.xip.fc_data_input
        soc.xip.fc_data_output = soc.soc_ico.input
        soc.soc_ico.input = soc.soc_ico.hb_ico.input
        soc.xip.fc_fetch_output = soc.soc_ico.input
        soc.soc_ico.input = soc.soc_ico.hb_ico.input

        # Refill connections to hyper devices
        soc.xip.refill_0 = soc.udma.refill_hyper0
        soc.xip.refill_1 = soc.udma.refill_hyper1


    
        # APB to peripherals bindings
        soc.apb_ico.stdout = soc.stdout.input
    
        flls_config = tp.get('soc/peripherals/flls')
  
        for fll_name, fll_config in flls_config.get_items().items():
          soc.apb_ico.set(fll_name, soc.get(fll_name).input)

          clocks = fll_config.get("clocks").get_dict()

          for i in range(0, len(clocks)):

            target = clocks[i]
            clock_itf = 'clock_' + str(i)

            if target == 'soc':
              soc.get(fll_name).set(clock_itf, soc.fll_soc_clock)
            elif target == 'cluster':
              for cid in range(0, nb_cluster):
                soc.get(fll_name).set(clock_itf, soc.new_itf(get_cluster_name(cid) + '_fll'))
            elif target == 'periph':
              soc.periph_clock = Component(properties=OrderedDict([
                ('vp_class', "vp/clock_domain"),
                ('vp_component', "vp.clock_domain_impl"),
                ('frequency', 50000000)
              ]))
              soc.periph_clock_dual_edges = Component(properties=OrderedDict([
                ('vp_class', "vp/clock_domain"),
                ('vp_component', "vp.clock_domain_impl"),
                ('frequency', 100000000),
                ('factor', 2)
              ]))
              soc.get(fll_name).set(clock_itf, soc.periph_clock.clock_in)
              soc.get(fll_name).set(clock_itf, soc.periph_clock_dual_edges.clock_in)
              if has_udma:
                soc.periph_clock.out = soc.udma.periph_clock
                soc.periph_clock_dual_edges.out = soc.udma.periph_clock_dual_edges
  
    
        if has_udma:
          soc.apb_ico.udma = soc.udma.input
    
        if has_soc_events:
          soc.event = soc.soc_eu.event_in
          soc.apb_ico.soc_eu = soc.soc_eu.input
          
        soc.apb_ico.apb_soc_ctrl = soc.apb_soc_ctrl.input
    
        if has_rtc:
          soc.wakeup_rtc = soc.apb_soc_ctrl.wakeup_rtc
          soc.wakeup_rtc = soc.fc_itc.in_event_16
    
          rtc_irq = fc_events.get_child_int('evt_rtc')
          rtc_apb_irq = fc_events.get_child_int('evt_rtc_apb')
    
          if rtc_irq is not None:
            soc.wakeup_rtc = soc.fc_itc.new_itf('in_event_%d' % (rtc_irq))
    
          if rtc_apb_irq is not None:
            soc.rtc_apb_irq = soc.fc_itc.new_itf('in_event_%d' % (rtc_apb_irq))
    
        if has_pmu:
          soc.apb_soc_ctrl.wakeup_out = soc.wakeup_out
          soc.apb_soc_ctrl.wakeup_seq = soc.wakeup_seq
    
    
        if has_fc:
    
          if has_soc_events:
            soc.ref_clock = soc.soc_eu.ref_clock
            soc.soc_eu.ref_clock_event = soc.fc_itc.new_itf('in_event_%d' % fc_events.get_child_int('evt_clkref'))
    
    
          soc.apb_ico.fc_itc = soc.fc_itc.input
          if has_fc and tp.get_child_int("soc/peripherals/fc_dbg_unit/version") <= 1:
              soc.apb_ico.fc_dbg_unit = soc.fc.dbg_unit
          if has_fc_icache:
              soc.apb_ico.fc_icache = soc.fc_icache_ctrl.input
    
        if has_fc_tcdm:
          soc.fc_ico.fc_tcdm = soc.fc_tcdm.input
    
        # Soc interco
        soc.soc_ico.apb = soc.apb_ico.input
        soc.soc_ico.axi_master = soc.axi_ico.input
    
        if l2_is_partitioned:
          soc.soc_ico.l2_shared_0 = soc.l2_shared_0.input
          soc.soc_ico.l2_shared_1 = soc.l2_shared_1.input
          soc.soc_ico.l2_shared_2 = soc.l2_shared_2.input
          soc.soc_ico.l2_shared_3 = soc.l2_shared_3.input
          soc.soc_ico.l2_priv0 = soc.l2_priv0.input
          soc.soc_ico.l2_priv1 = soc.l2_priv1.input
        else:
          soc.soc_ico.l2 = soc.l2.input
    
        if has_rtc:
          soc.rtc_event_in = soc.soc_eu.event_in
    
        if has_rtc:
          if rtc_version is not None and rtc_version >= 2:
            soc.apb_soc_ctrl.rtc = soc.rtc_input
          else:
            soc.apb_ico.rtc = soc.rtc_input
    
        # APB SOC
        if has_fast_clock:
          soc.fast_clock = soc.apb_soc_ctrl.fast_clock
          soc.ref_clock = soc.apb_soc_ctrl.ref_clock
          soc.fast_clock_out = soc.udma.fast_clock
        if has_fc:
          soc.apb_soc_ctrl.bootaddr = soc.fc.bootaddr
        if has_udma:
          soc.apb_soc_ctrl.event = soc.soc_eu.event_in
        if has_pmu and has_fc:
            if fc_events.get_child_int('evt_cluster_pok') is not None:
              soc.apb_soc_ctrl.cluster_power_irq = soc.fc_itc.new_itf('in_event_%d' % fc_events.get_child_int('evt_cluster_pok'))
              soc.apb_soc_ctrl.cluster_clock_gate_irq = soc.fc_itc.new_itf('in_event_%d' % fc_events.get_child_int('evt_cluster_cg_ok'))
    
        # ROM
        if has_rom:
          soc.apb_ico.rom = soc.rom.input
    
        # PMU
        if has_pmu:
          soc.apb_ico.pmu = soc.pmu_input
    
        # EFUSE
        if has_efuse:
          soc.apb_ico.efuse = soc.efuse.input
    
        # FC
        if has_fc:
          if has_fc_icache:
            soc.fc.fetch = soc.fc_icache.input_0
            soc.fc_icache.refill = soc.soc_ico.fc_fetch
          else:
            soc.fc.fetch = soc.soc_ico.fc_fetch
    
          fc_tohost = tp.get_str('soc/fc/riscv_fesvr_tohost_addr')
    
          if fc_tohost is not None:
            soc.bus_watchpoint = Component(properties=OrderedDict([
                ('@includes@', ["ips/interco/bus_watchpoint.json"]),
                ('riscv_fesvr_tohost_addr', fc_tohost)
            ]))
            soc.fc.data = soc.bus_watchpoint.input
            soc.bus_watchpoint.output = soc.soc_ico.fc_data
          else:
            soc.fc.data = soc.soc_ico.fc_data
    
    
          soc.fc.irq_ack = soc.fc_itc.irq_ack
    
        # AXI
        if has_cluster:
          for cid in range(0, nb_cluster):
            cluster_name = get_cluster_name(cid)
            soc.axi_ico.set(cluster_name, soc.new_itf(cluster_name + '_input'))
        soc.axi_ico.soc = soc.soc_ico.axi_slave
    
        if has_ddr:
          soc.axi_ico.ddr = soc.ddr
    
        # FC ITC
        if has_fc:
            soc.fc_itc.irq_req = soc.fc.irq_req
    
        # PMU
        if has_fc:
            soc.scu_ok = soc.fc_itc.in_event_25
            soc.picl_ok = soc.fc_itc.in_event_24
    
        # Cluster
        if has_cluster:
          if has_fc:
              soc.dma_irq = soc.fc_itc.in_event_8
          soc.soc_input = soc.axi_ico.input
    
    
        # UDMA
        if has_udma:
          soc.udma.l2_itf = soc.soc_ico.udma_tx
          soc.udma.event_itf = soc.soc_eu.event_in
          for itf in udma_conf.get('interfaces').get():
            itf_conf = udma_conf.get(itf.get())
            nb_channels = itf_conf.get_child_str('nb_channels')
            is_master = itf_conf.get_child_bool('is_master')
            is_slave = itf_conf.get_child_bool('is_slave')
            is_dual = itf_conf.get_child_bool('is_dual')
            for channel in range(0, nb_channels):
              itf_name = itf.get() + str(channel)
    
              if is_master:
                soc.udma.set(itf_name, soc.new_itf(itf_name))
              if is_slave:
                if is_dual:
                  soc.set(itf.get() + str(channel*2), soc.udma.new_itf(itf.get() + str(channel*2)))
                  soc.set(itf.get() + str(channel*2+1), soc.udma.new_itf(itf.get() + str(channel*2+1)))
                else:
                  soc.set(itf_name, soc.udma.new_itf(itf_name))
    
    
        if tp.get('**/gdbserver') is not None:
          soc.gdbserver.out = soc.soc_ico.debug
    
        # Soc EU
        if has_fc:
            soc.soc_eu.fc_event_itf = soc.fc_itc.soc_event
    
        if taps_conf is not None:
          soc.jtag0 = taps[0].jtag_in
          taps[-1].jtag_out = soc.jtag0_out
          for index in range(1, len(taps)):
            taps[index -1].jtag_out = taps[index].jtag_in
    
          for tap in taps:
            if tap.get_config().get_bool('has_io_port'):
              tap.io = soc.soc_ico.debug
            if tp.get_child_bool('**/apb_soc_ctrl/has_jtag_reg'):
              if tap.get_config().get_bool('has_confreg'):
                soc.apb_soc_ctrl.confreg_soc = tap.confreg_soc
                tap.confreg_ext = soc.apb_soc_ctrl.confreg_ext
    
        # Interrupts
        for name, irq in fc_events_dict.items():
          if len(name.split('.')) == 2:
            comp_name, itf_name = name.split('.')
            if has_fc_eu:
              comps[comp_name].set(itf_name, soc.fc_eu.new_itf('in_event_%d_pe_0' % irq))
            else:
              comps[comp_name].set(itf_name, soc.fc_itc.new_itf('in_event_%d' % irq))
    
    
    
        # Loader
        soc.plt_loader.out = soc.soc_ico.debug
    
    
        if tp.get('soc/job_fifo') is not None:
            soc.job_fifo = Component(properties=OrderedDict([
                ('@includes@', ["chips/oprecompkw_sa/job_fifo.json"])
            ]))
            soc.job_fifo_injector = Component(properties=OrderedDict([
                ('@includes@', ["tools/vp/injector.json"])
            ]))
    
            soc.host_injector = Component(properties=OrderedDict([
                ('@includes@', ["tools/vp/injector.json"])
            ]))
    
            soc.apb_ico.get_property('mappings')["job_fifo"] = OrderedDict([("base", "0x1A120000"), ("size", "0x00001000"), ("remove_offset", "0x1A120000")])
            soc.apb_ico.job_fifo = soc.job_fifo.input
            soc.job_fifo_injector.output = soc.job_fifo.fifo
    
            soc.axi_ico.get_property('mappings')["ext"] = OrderedDict([
              ("base", "0x1000000000000"), ("size", "0x1000000000000")
            ])
            soc.axi_ico.ext = soc.host_injector.input
    
            soc.job_fifo.irq = soc.job_fifo_irq
    
        if chip == 'wolfe' or chip == 'vega' or chip == 'gap9' or chip == 'gap9_v2':
          soc.bootsel = soc.apb_soc_ctrl.bootsel
    
    
        self.soc = soc
    
        self.soc.apb_soc_ctrl.fast_clk_ctrl = self.soc.fast_clk_ctrl
        self.soc.apb_soc_ctrl.ref_clk_ctrl = self.soc.ref_clk_ctrl


    def gen(self):

        return self.soc
