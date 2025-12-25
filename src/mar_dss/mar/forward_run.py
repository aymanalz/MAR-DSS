from typing import Any, Dict
# import mar_dss.app.utils.data_storage as data_storage
from mar_dss.mar import hard_constraints as hc_module
from mar_dss.mar import soft_constraints as sc_module
from mar_dss.mar import benefits as benefits_module
from mar_dss.mar.dss import DecisionSupportSystem
from mar_dss.mar.options import mar_options

def forward_run():
    mar_options_list = mar_options()

    class DssResult:
        pass
    results = {}
    filters = {}
    for option in mar_options_list:
        hc_list = hc_module.hard_constraints(option)
        sc_list = sc_module.soft_constraints(option)
        benefits_list = benefits_module.benefits(option)

        dss_instance = DecisionSupportSystem(hc_list, sc_list, benefits_list)
        results[option.name] = dss_instance.evaluate(option)
        filters[option.name] = {'hard': hc_list, 'soft': sc_list, 'benefits': benefits_list}
    dss_result = DssResult()
    dss_result.results = results
    dss_result.filters = filters
    return dss_result
