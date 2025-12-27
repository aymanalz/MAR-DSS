from typing import Any, Dict, Optional
# import mar_dss.app.utils.data_storage as data_storage
from mar_dss.mar import hard_constraints as hc_module
from mar_dss.mar import soft_constraints as sc_module
from mar_dss.mar import benefits as benefits_module
from mar_dss.mar.dss import DecisionSupportSystem
from mar_dss.mar.options import mar_options

def forward_run(cost_override: Optional[Dict[str, float]] = None):
    """
    Run DSS evaluation for all MAR options.
    
    Args:
        cost_override: Optional dictionary mapping option names to cost values.
                      If provided, overrides the base_cost for each option.
                      Format: {"Surface Recharge": 1500000, "Dry Well": 2000000, ...}
    
    Returns:
        DssResult object with results and filters
    """
    mar_options_list = mar_options()
    
    # Apply cost override if provided
    if cost_override:
        for option in mar_options_list:
            if option.name in cost_override:
                option.base_cost = float(cost_override[option.name])
                print(f"Updated {option.name} base_cost to ${option.base_cost:,.0f}")

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
