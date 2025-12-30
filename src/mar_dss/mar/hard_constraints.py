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
        why = "Unconfined aquifer is suitable for surface recharge"
    else:
        if option.name == "Spreading Basins":
            check = False
            why = f"Spreading basins are not suitable for recharging {aquifer_type} aquifer"
        else:
            check = True
            why = "Spreading basins are suitable for recharging {aquifer_type} aquifer"
    initial_surface_rechargeability = {
        "name": "Surface rechargeability intial feasibility",
        "pass": True,
        "why": why
    }
    constraints.append(initial_surface_rechargeability)

    # ==================================================================
    # Recharge Efficiency
    # ==================================================================
    rechargable_percentage = graph.get_node_value('rechargability')
    if rechargable_percentage is None:
        rechargable_percentage = 0  
    confined_rechargability = graph.get_node_value('confined_rechargability')
    if confined_rechargability is None:
        confined_rechargability = 0
    if aquifer_type.lower() == "Unconfined".lower():
        if rechargable_percentage < defaults['maximum_rechargability']:
            check = False
            why = f"Rechargeable percentage {round(rechargable_percentage, 2)}% is less than the maximum rechargeable percentage {defaults['maximum_rechargability']}"
        else:
            check = True
            why = f"Rechargeable percentage {round(rechargable_percentage, 2)}% is greater than the maximum rechargeable percentage {defaults['maximum_rechargability']}"
    else:
        if confined_rechargability < defaults['maximum_rechargability']:
            check = False
            why = f"Confined rechargeable percentage {round(confined_rechargability, 2)}% is less than the maximum rechargeable percentage {defaults['maximum_rechargability']}"
        else:
            check = True
            why = f"Confined rechargeable percentage {round(confined_rechargability, 2)}% is greater than the maximum rechargeable percentage {defaults['maximum_rechargability']}"
    
    recharge_efficiency_metric = {
        "name": "Recharge Efficiency",
        "pass": check,
        "why": why
       
    }
    constraints.append(recharge_efficiency_metric)

    
    return constraints