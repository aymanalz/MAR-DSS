from typing import Any, Dict, List
from mar_dss.mar.options import MAROption
import mar_dss.app.utils.data_storage as data_storage

def benefits(option: MAROption) -> List[Dict[str, float]]:
    """Generate benefit metrics for MAR options."""

    benefits_list = []
    graph = data_storage.get_data("decision_graph")
    aquifer_type = graph.get_node_value('aq_type') # ['Unconfined', 'Confined', 'Semi-confined', 'Karstic', 'Fractured', 'Other']

    # ==================================================================
    # 1. Volume of source water that can be recharged
    # ==================================================================
    rechargable_percentage = graph.get_node_value('rechargability')
    confined_rechargability = graph.get_node_value('confined_rechargability')
    if aquifer_type.lower() == "Unconfined".lower():        
        value = rechargable_percentage/100
        weight = 100
    else: # confined       
       value = confined_rechargability/100
       weight = 100

    source_water_volume_rechargable = {
        "name": "Recharge Efficiency",
        "value": value,
        "weight": weight
    }
    benefits_list.append(source_water_volume_rechargable)

  
   

    # normalize weights to 1
    total_weight = sum(benefit["weight"] for benefit in benefits_list)
    for benefit in benefits_list:
        benefit["weight"] = benefit["weight"] / total_weight

    return benefits_list
