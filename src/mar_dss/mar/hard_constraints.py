# hard constraints for mar options

from typing import Any, Dict, List
from mar_dss.mar.options import MAROption
import mar_dss.app.utils.data_storage as data_storage
from mar_dss.rules.defaults import defaults

def hard_constraints(option: MAROption) -> List[Dict[str, bool]]:
    """Generate hard constraints for MAR options."""
   
    constraints = []
    graph = data_storage.get_data("decision_graph")
    aquifer_type = graph.get_node_value('aq_type')  # ['Unconfined', 'Confined', 'Semi-confined', 'Karstic', 'Fractured', 'Other']

    # ==================================================================
    # Surface rechargeability
    # ==================================================================   
    if aquifer_type.lower() == "Unconfined".lower():
        check = True
    else:
        if option.name == "Spreading Basins":
            check = False
        check = True
    initial_surface_rechargeability = {
        "name": "Surface rechargeability intial feasibility",
        "pass": True
    }
    constraints.append(initial_surface_rechargeability)

    # ==================================================================
    # Recharge Efficiency
    # ==================================================================
    rechargable_percentage = graph.get_node_value('rechargability')
    confined_rechargability = graph.get_node_value('confined_rechargability')
    if aquifer_type.lower() == "Unconfined".lower():
        if rechargable_percentage < defaults['maximum_rechargability']:
            check = False
        else:
            check = True
    else:
        if confined_rechargability < defaults['maximum_rechargability']:
            check = False
        else:
            check = True
    
    recharge_efficiency_metric = {
        "name": "Recharge Efficiency",
        "pass": check
       
    }
    constraints.append(recharge_efficiency_metric)

    
    return constraints