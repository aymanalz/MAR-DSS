
from typing import Any, Dict, List
from mar_dss.mar.options import MAROption
import mar_dss.app.utils.data_storage as data_storage

hardend_constraints =[]
levels = {
    0: "Acceptable",
    1: "Acceptable with additional Cost",
    2: "Warning",
    3: "Mitigation",
    4: "Reject",
}

def soft_constraints(option: MAROption) -> List[Dict[str, Any]]:
    """Generate soft constraints for MAR options."""
    

    constraints = []
    graph = data_storage.get_data("decision_graph")
    aquifer_type = graph.get_node_value('aq_type') # ['Unconfined', 'Confined', 'Semi-confined', 'Karstic', 'Fractured', 'Other']
    
    
    # ==================================================================
    # 1. ground surface slope
    # ==================================================================    
    slope_significance = graph.get_node_value('gs_slope_significance')
    if slope_significance == "Gentle":
        response = 0
        penalty = []
    elif slope_significance == "Moderate":
        if option.name == "Spreading Basins":
            response = 1
            penalty = ["Cost: Moderate extra cost for earthwork to mitigate slope"]
        else:
            response = 0
            penalty = []
    elif slope_significance == "Steep":
        if option.name == "Spreading Basins":
            response = 3
            penalty = ["Cost: Significant extra cost for earthwork to mitigate slope"]
        else:
            response = 0
            penalty = []
    
    if option.name in ["Dry Wells", "Injection Wells"]:
        response = 1
        penalty = ["Cost: Moderate extra cost for earthwork to mitigate slope"]
   
    
    ground_surface_slope = {
        "name": "Ground surface slope Suitability",
        "response": response,   # 0–4
        "penalty": penalty,
        "type": "hydrogeologic",
        "hard": True if "Ground surface slope Suitability" in hardend_constraints else False
    }
    constraints.append(ground_surface_slope)

    # ==================================================================
    # 2. restrictive vadose zone infiltration
    # ==================================================================
    high_infiltration = graph.get_node_value('k_vadose_threshold')
    if (high_infiltration):
        response = 0
        penalty = []
    else:
        if option.name == "Spreading Basins":
            response = 3
            penalty = ["Cost: Consider bypassing vadose zone infiltration"]
        else:
            response = 0
            penalty = []
            
    vadose_infiltration = {
        "name": "Vadose zone infiltration",
        "response": response,   # 0–4
        "penalty": penalty,
        "type": "hydrogeologic",
        "hard": True if "Vadose zone infiltration" in hardend_constraints else False
    }
    constraints.append(vadose_infiltration)

     # ==================================================================
    # 3. vadose zone pollution
    # ==================================================================

    vadose_pollution = graph.get_node_value('vadose_pollution_present')
    if not (vadose_pollution):
        response = 0
        penalty = []
    else:
        if option.name == "Spreading Basins":
            response = 3
            penalty = ["Cost: Consider bypassing vadose zone pollution or remediation"]
        else:
            response = 0
            penalty = []       
        
    vadose_pollution_metric = {
        "name": "Vadose zone pollution",
        "response": response,   # 0–4
        "penalty": penalty, 
        "type": "hydrogeologic",
        "hard": True if "Vadose zone pollution" in hardend_constraints else False
    }
    constraints.append(vadose_pollution_metric)
    
    # ==================================================================
    # 4. vadose_biodegradable
    # ==================================================================
    vadose_biodegradable = graph.get_node_value('vadose_biodegradable')
    if vadose_biodegradable:
        if option.name == "Spreading Basins":
            response = 2 # warning
            penalty = ["Warning: Vadose zone pollution is biodegradable, ensure natural attenuation is monitored"]
        else:
            response = 0
            penalty = []
    else:
        if option.name == "Spreading Basins":
            response = 3
            penalty = ["Cost: Consider bypassing vadose zone pollution or remediation"]
        else:            
            response = 2 # warning
            penalty = ["Action: Toxic contamination in the vadose. Although can be bypassed, mounding water table may mobilize contaminants to the aquifer"]
    vadose_biodegradable_metric = {
        "name": "Vadose zone pollution biodegradability",
        "response": response,   # 0–4
        "penalty": penalty,
        "type": "hydrogeologic",
        "hard": True if "Vadose zone biodegradability" in hardend_constraints else False
    }
    constraints.append(vadose_biodegradable_metric)
    
    # ==================================================================
    # 5. vadose zone remediation
    # ==================================================================
    vadose_remediation = graph.get_node_value('vadose_remediation_needed')
    if vadose_remediation:
        if option.name == "Spreading Basins":
            response = 3
            penalty = ["Cost: Consider bypassing vadose zone or remediation"]
        else:
            response = 0
            penalty = []
    else:
        response = 0
        penalty = []
    vadose_remediation_needed = {
        "name": "Vadose zone remediation needed",
        "response": response,   # 0–4
        "penalty": penalty,
        "type": "hydrogeologic",
        "hard": True if "Vadose zone remediation needed" in hardend_constraints else False
    }
    constraints.append(vadose_remediation_needed)

    # ==================================================================
    # 6. vadose zone residence time
    # ==================================================================
    vadose_residence_time = graph.get_node_value('vadose_residence_time')
    residence_time_issues = graph.get_node_value('vadose_residence_time_issues')
    if vadose_residence_time is None:
        response = 0
        penalty = []
    else:
        if residence_time_issues is not None and len(residence_time_issues) > 0:
            response = 3
            penalty = [f"Mitigation: Vadose zone residence time ({vadose_residence_time} days) is not reasonable for {', '.join(residence_time_issues)}"]
        else:
            response = 2
            penalty = [f"Warning: Vadose zone residence time ({vadose_residence_time} days) is reasonable but careful monitoring is needed"]
 
    vadose_residence_time_metric = {
        "name": "Vadose zone residence time",
        "response": response,   # 0–4
        "penalty": penalty,
        "type": "hydrogeologic",
        "hard": True if "Vadose zone residence time" in hardend_constraints else False
    }
    constraints.append(vadose_residence_time_metric)

    # ==================================================================
    # 7. surface recharge suitability
    # ==================================================================
    surface_recharge_suitability = graph.get_node_value('surface_recharge_suitability')
    if surface_recharge_suitability is None:
        response = 0
        penalty = []
    else:
        if surface_recharge_suitability:
            response = 0
            penalty = []
        else:
            response = 3
            penalty = ["Mitigation: Surface recharge is likely not suitable because of ground slope, infiltration, or vadose zone contamination"]
    surface_recharge_suitability_metric = {
        "name": "Surface recharge suitability",
        "response": response,   # 0–4
        "penalty": penalty,
        "type": "hydrogeologic",
        "hard": True if "Surface recharge suitability" in hardend_constraints else False
    }
    constraints.append(surface_recharge_suitability_metric)

    # ==================================================================
    # 8. confined aquifer depth
    # ==================================================================
    confined_aquifer_depth = graph.get_node_value('confined_aquifer_depth')
    if confined_aquifer_depth is None:
        response = 0
        penalty = []
    else:
        if aquifer_type.lower() == "confined":
            if confined_aquifer_depth == "Too Deep":
                response = 4
                penalty = ["Reject :: Confined aquifer depth is too deep"]
            elif confined_aquifer_depth == "Moderate Deep":
                response = 2
                penalty = ["Cost: Confined aquifer depth is moderate deep"]
            else:
                response = 0
                penalty = []
        else:
            response = 0
            penalty = []
    confined_aquifer_depth_metric = {
        "name": "Confined aquifer depth Suitability",
        "response": response,   # 0–4
        "penalty": penalty, 
        "type": "hydrogeologic",
        "hard": True if "Confined aquifer depth" in hardend_constraints else False
    }
    constraints.append(confined_aquifer_depth_metric)

    # ==================================================================
    # leakage significance
    # ==================================================================
    leakage_significance = graph.get_node_value('leakage_significance')
    if aquifer_type.lower() == "unconfined":
        response = 0
        penalty = []
    else: # confined
        if leakage_significance == "Low":
            response = 0
            penalty = []
        elif leakage_significance == "Medium":
            response = 2
            penalty = ["Warning: Confined leakage is moderate"]            
        elif leakage_significance == "High":
            response = 3
            penalty = ["Mitigation: Confined leakage is significant"]
        
    leakage_significance_metric = {
        "name": "Confined leakage significance",
        "response": response,   # 0–4
        "penalty": penalty, 
        "type": "hydrogeologic",
        "hard": True if "Confined leakage significance" in hardend_constraints else False
    }
    constraints.append(leakage_significance_metric)


    return constraints