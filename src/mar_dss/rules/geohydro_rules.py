import numpy as np
import pandas as pd
from mar_dss.rules.analytical_solutions import compute_recharge_rate, theis_drawdown_or_Q
from mar_dss.rules.defaults import defaults
    




def is_unconfined(aq_type):
    if aq_type.lower() == "unconfined":
        return True
    else:
        return False

def is_confined(aq_type):
    if aq_type.lower() == "confined":
        return True
    else:
        return False

def find_limiting_layer(strat_df, unconfined, monthly_gw_depth):
    """ the limiting layer is in the vadose zone, so it is lowest k above water table"""
    if unconfined:
        cumulative_depth = strat_df["thickness"].cumsum()
        
        limiting_layer = []
        depth = np.mean(monthly_gw_depth)
        diff = cumulative_depth - depth
        # find the index of the smallest positive difference
        positive_diff = diff[diff > 0]
        wt_idex = positive_diff.idxmin()+1
        df_ = strat_df.iloc[0:wt_idex]           
        limit_layer_index = df_["K"].argmin()       
            
        return limit_layer_index
    else:
        return None # irrelevant for confined aquifer

def find_min_k_vadose_zone(strat_df, limiting_layer):
    if limiting_layer is None:
        return None # irrelevant for confined aquifer
    return strat_df.iloc[limiting_layer]["K"]

def check_k_vadose_threshold(k_min_vadose):
    """
    Check if vadose zone minimum hydraulic conductivity meets threshold for infiltration.
    
    Parameters:
    - k_min_vadose: Minimum hydraulic conductivity in vadose zone (ft/day)
    
    Returns:
    - True if k_min_vadose >= threshold (suitable for infiltration)
    - False if k_min_vadose < threshold or is None
    """
    if k_min_vadose is None:
        return False
    threshold = defaults["k_min_vadose_threshold"]
    return k_min_vadose >= threshold

def check_vadose_pollution(unconfined, vadose_polluted_present):
    if not (unconfined):
        return None # irrelevant for confined aquifer
    if vadose_polluted_present is None:
        return None

    if vadose_polluted_present:
        return True
    else:
        return False

def check_vadose_high_toxicity(vadose_pollution_present, vadose_pollution_high_toxicity):
    """
    Check if highly toxic contaminants are present in the vadose zone.
    
    Parameters:
    - vadose_pollution_present: Boolean indicating if pollution is present
    - vadose_pollution_high_toxicity: Boolean flag indicating high toxicity presence
    
    Returns:
    - True if highly toxic contaminants are present
    - False if no high toxicity or not applicable
    - None if no pollution present (irrelevant)
    """
    if  vadose_pollution_present is None:
        return None  # irrelevant for confined aquifer

    if vadose_pollution_high_toxicity:
        return True
    else:
        return False

def check_vadose_biodegradable(vadose_pollution_present, vadose_pollution_high_toxicity):
    if vadose_pollution_high_toxicity is None:
        return None # irrelevant for confined aquifer
    if vadose_pollution_present and not vadose_pollution_high_toxicity:
        return True
    else:
        return False
    
def check_vadose_remediation(vadose_pollution_high_toxicity):
    """
    Check if vadose zone remediation is available, completed, or feasible.
    
    Parameters:
    - vadose_pollution_present: Boolean indicating if pollution is present
    - vadose_remediation_data: Boolean, string, or dict indicating remediation status
    
    Returns:
    - True if remediation is available/completed/feasible
    - False if remediation is not available or not needed
    - None if no pollution present (remediation not applicable)
    """
    if vadose_pollution_high_toxicity is None:
        return None # irrelevant for confined aquifer
    if vadose_pollution_high_toxicity:
        return True
    else:
        return False




def check_topsoil_limiting(limiting_layer, k_min_vadose):
    if limiting_layer == 0 and k_min_vadose < defaults["k_min_vadose_threshold"]:
        return True 
    else:
        return False

def check_topsoil_removable(top_soil_limiting, strat_df):
    
    if top_soil_limiting:
        top_soil_thickness = strat_df["thickness"].values[0]
        if top_soil_thickness < 6:
            return True
        else:
            return False
    else:
        return None # irrelevant if top soil is not limiting
def compute_min_gw_depth(limiting_layer, strat_df, d_gw_min):
   
    if limiting_layer is None:
        return None # irrelevant for confined aquifer
    d_gw_min = float(d_gw_min)    
    limiting_layer = int(limiting_layer)
    k_min_vadose = strat_df.iloc[limiting_layer]["K"]
    if k_min_vadose >= defaults["k_min_vadose_threshold"]:        
        return d_gw_min
    else:
        layer_bottom_depth = strat_df["thickness"].cumsum()
        limiting_layer_bottom_depth = layer_bottom_depth.iloc[limiting_layer]
        return max(d_gw_min, limiting_layer_bottom_depth)



def compute_spread_area(k_min_vadose, max_available_area, gw_depth, source_water_volume, strat_df, limiting_layer, op_gw_depth, top_soil_removable):

    if top_soil_removable is None:
        # None means irrelevant, False means not removable, True means removable
        pass
    else:
        if top_soil_removable:
            pass
        else:
            # not removable, so no spread area
            return None

    if k_min_vadose is None:
        return None # irrelevant for confined aquifer
   

    max_available_area = float(max_available_area)
    k_min_vadose = float(k_min_vadose)
    avg_gw_depth = np.mean(gw_depth)
    limiting_layer = int(limiting_layer)
    

    layer_depths = strat_df['thickness'].cumsum()

    saturated_layres = layer_depths - avg_gw_depth
    saturated_layres = saturated_layres[saturated_layres>0]
    saturated_thickness = saturated_layres.sum()
    sat_thks = saturated_layres.diff()
    sat_thks.iloc[0] = saturated_layres.iloc[0]

    sy_s = strat_df.iloc[-(len(sat_thks)):]['sy/ss']
    k_s = strat_df.iloc[-(len(sat_thks)):]['K']
    k_mean = (k_s.values * sat_thks.values).sum() / sat_thks.values.sum()
    sy_mean = (sy_s.values * sat_thks.values).sum() / sat_thks.values.sum()

    dh = avg_gw_depth - op_gw_depth

    t = 50 # long time for near steady state

    # todo: Talk to run to check if the average is the best way to estimate the spread area.
    vol_max_available = (np.max(source_water_volume)/30.25)
    vol_possiblee = vol_max_available
    spread_area =  vol_max_available / (k_min_vadose)
    
    # Iterative calculation to find appropriate spread area
    max_iterations = 100  # Safety limit
    iteration = 0
    while iteration < max_iterations:
        spread_area = vol_possiblee / k_min_vadose
        area = min(spread_area, max_available_area)
        infl_rate = compute_recharge_rate(x=0, y=0,
                                         t=t, del_h=dh,
                                         spread_area=area,
                                         k=k_mean,
                                         b=saturated_thickness, 
                                         sy=sy_mean)
        if infl_rate <= k_min_vadose:
            infl_rate = k_min_vadose
            break
        else:
            vol_possiblee = vol_possiblee * 0.99
      
        # vol = spread_area * infl_rate
        # if (infl_rate < k_min_vadose):  
        #    if vol<vol_max_available:
        #         spread_area = spread_area * k_min_vadose/infl_rate
                
        #    else:
        #         spread_area = spread_area * infl_rate/k_min_vadose
        #    spread_area = min(spread_area, max_available_area)
        # else:
        #     # If spread area is too large, reduce it
        #     spread_area = spread_area * infl_rate/ k_min_vadose 
        
            
            
        # iteration += 1

        # if (infl_rate <= k_min_vadose) and (vol/vol_max_available >= 0.95):
        #     break
    
    # Ensure we don't exceed max available area
    # if spread_area > max_available_area:
    #         spread_area = max_available_area
    # if infl_rate > k_min_vadose:
    #     infl_rate = k_min_vadose
            
    return {"spread_area": spread_area, "infl_rate": infl_rate, "inf_k_ratio": infl_rate/k_min_vadose}

def compute_number_of_injection_wells(source_water_volume, op_gw_depth, strat_df, gw_depth, Hmax, confined, unconfined):
    if confined:
        if len(strat_df) != 4:
            raise ValueError("Stratigraphy table must have four layers for confined aquifer")
        
        kaq = strat_df.iloc[2]["K"]
        B = strat_df.iloc[2]["thickness"]
        Ss = strat_df.iloc[2]["sy/ss"]
        transmissivity = kaq * B
        Ss = Ss * B
        Qmax = defaults["max_injection_Q_per_well"] 
        max_Q_per_well = theis_drawdown_or_Q(Q_or_dh=Hmax, T=transmissivity, S=Ss, r=1, t=50, compute_Q=True)
        Q_per_well = min(Qmax, max_Q_per_well)     
        number_of_wells = np.ceil((np.max(source_water_volume)/30.25) / Q_per_well)       
        number_of_wells =min(defaults["max_number_of_injection_wells"], number_of_wells)
        return {"number_of_wells": number_of_wells, "Q_per_well": Q_per_well} 

        
      
    if unconfined:
        # thiem equation
        avg_gw_depth = np.mean(gw_depth)
        layer_depths = strat_df['thickness'].cumsum()

        saturated_layres = layer_depths - avg_gw_depth
        saturated_layres = saturated_layres[saturated_layres>0]
        saturated_thickness = saturated_layres.sum()
        sat_thks = saturated_layres.diff()
        sat_thks.iloc[0] = saturated_layres.iloc[0]

        sy_s = strat_df.iloc[-(len(sat_thks)):]['sy/ss']
        k_s = strat_df.iloc[-(len(sat_thks)):]['K']
        k_mean = (k_s.values * sat_thks.values).sum() / sat_thks.values.sum()
        sy_mean = (sy_s.values * sat_thks.values).sum() / sat_thks.values.sum()
        dh = avg_gw_depth - op_gw_depth

        # corrected drawdown for unconfined aquifer
        dh_corrected = dh - dh*dh/(2.0*saturated_thickness)
        transmissivity = k_mean * saturated_thickness
        Ss = sy_mean * saturated_thickness
        max_Q_per_well = theis_drawdown_or_Q(Q_or_dh=dh_corrected, T=transmissivity, S=Ss, r=1, t=50, compute_Q=True)

        #max_Q_per_well = (2 * 3.14159 * k_mean*saturated_thickness*dh) / (np.log(300))
        Qmax = defaults["max_injection_Q_per_well"] #  ft^3/day, arround 20L/sec
        Q_per_well = min(max_Q_per_well, Qmax)
        number_of_wells = np.ceil((np.max(source_water_volume)/30.25) / Q_per_well)
        number_of_wells =min(defaults["max_number_of_injection_wells"], number_of_wells)
                                        
        return {"number_of_wells": number_of_wells, "Q_per_well": Q_per_well} # irrelevant for unconfined aquifer
    
def compute_number_of_dry_wells(source_water_volume, op_gw_depth, strat_df, gw_depth, unconfined):
    if unconfined:
        # thiem equation
        avg_gw_depth = np.mean(gw_depth)
        layer_depths = strat_df['thickness'].cumsum()

        saturated_layres = layer_depths - avg_gw_depth
        saturated_layres = saturated_layres[saturated_layres>0]
        saturated_thickness = saturated_layres.sum()
        sat_thks = saturated_layres.diff()
        sat_thks.iloc[0] = saturated_layres.iloc[0]

        sy_s = strat_df.iloc[-(len(sat_thks)):]['sy/ss']
        k_s = strat_df.iloc[-(len(sat_thks)):]['K']
        k_mean = (k_s.values * sat_thks.values).sum() / sat_thks.values.sum()
        sy_mean = (sy_s.values * sat_thks.values).sum() / sat_thks.values.sum()
        dh = avg_gw_depth - max(op_gw_depth, defaults["max_drywell_depth_ft"])
        if dh <=0:
            return {"number_of_dry_wells": 0, "Q_per_dry_well": 0}
        # corrected drawdown for unconfined aquifer
        dh_corrected = dh - dh*dh/(2.0*saturated_thickness)
        transmissivity = k_mean * saturated_thickness
        Ss = sy_mean * saturated_thickness
        max_Q_per_well = theis_drawdown_or_Q(Q_or_dh=dh_corrected, T=transmissivity, S=Ss, r=1, t=50, compute_Q=True)

        #max_Q_per_well = (2 * 3.14159 * k_mean*saturated_thickness*dh) / (np.log(300))
        Qmax = defaults["max_injection_Q_per_well"] #  ft^3/day, arround 20L/sec
        Q_per_well = min(max_Q_per_well, Qmax)
        number_of_wells = np.ceil((np.max(source_water_volume)/30.25) / Q_per_well)
        number_of_wells =min(defaults["max_number_of_injection_wells"], number_of_wells)
                                        
        return {"number_of_dry_wells": number_of_wells, "Q_per_dry_well": Q_per_well} 
    else: # confined aquifer
        return {"number_of_dry_wells": 0, "Q_per_dry_well": 0}

def compute_annual_recharge_volume(design_sizing_result, source_water_volume):
    if design_sizing_result is None:
        return None # irrelevant for confined aquifer
    spread_area = design_sizing_result["spread_area"]
    infl_rate = design_sizing_result["infl_rate"]
    inf_k_ratio = design_sizing_result["inf_k_ratio"]

    annual_recharge_volume = 0
    # 30.25 is the number of days in a month
    for i in range(12):
        current_month_storage = spread_area * infl_rate * 30.25
        act_recharge =min(current_month_storage, source_water_volume[i])
        annual_recharge_volume += act_recharge

    return annual_recharge_volume   

def compute_annual_injection_volume(number_of_injection_wells_result, source_water_volume):
    if number_of_injection_wells_result is None:
        return None # irrelevant for confined aquifer
    number_of_wells = number_of_injection_wells_result["number_of_wells"]
    Q_per_well = number_of_injection_wells_result["Q_per_well"]
    annual_injection_volume = number_of_wells * Q_per_well * 365.25

    annual_injection_volume = min(annual_injection_volume, np.sum(source_water_volume))
    return annual_injection_volume

def compute_annual_dry_well_volume(number_of_dry_wells_result, source_water_volume):
    if number_of_dry_wells_result is None:
        return None # irrelevant for confined aquifer
    number_of_wells = number_of_dry_wells_result["number_of_dry_wells"]
    Q_per_dry_well = number_of_dry_wells_result["Q_per_dry_well"]
    annual_dry_well_volume = number_of_wells * Q_per_dry_well * 365.25
    annual_dry_well_volume = min(annual_dry_well_volume, np.sum(source_water_volume))
    return annual_dry_well_volume

def compute_vadose_residence_time(vadose_biodegradable, design_zing, strat_df,  avg_gw_depth):

    # Not applicable for confined aquifers
    #vadose_biodegradable = True # debug only
    if not vadose_biodegradable:
        return None
    # Calculate effective porosity from vadose zone layers
    # Use sy/ss from stratigraphy layers above water table
    #effective_porosity = defaults["vadose_effective_porosity"]  # default   

    layer_depths = strat_df['thickness'].cumsum()
    unsaturated_layres = layer_depths - np.mean(avg_gw_depth)
    unsaturated_layres = unsaturated_layres[unsaturated_layres<0]
    unsaturated_thickness = unsaturated_layres.abs().sum()
    #ks = strat_df.iloc[:(len(unsaturated_layres))]['K']

    
    # ratio = defaults["average_moisture_content"] / effective_porosity#
    # v = ks.values * ratio / effective_porosity# todo: v = k * i * theta, 
    
    infl_rate = design_zing["infl_rate"]
    v = infl_rate/defaults["average_moisture_content"]
    residence_time = unsaturated_thickness / v
    return residence_time

def check_vadose_residence_time_reasonable(vadose_residence_time):
    if vadose_residence_time is None:
        return None
    unreasonble = []
    if vadose_residence_time <= 7:
        unreasonble.append("Organic Matter")
    if vadose_residence_time <=30:
        unreasonble.append("Pathogenic Bacteria")
        unreasonble.append("Trace Organic Matter")
        unreasonble.append("Nutrients")

    return unreasonble    

def compute_rechargable_percentage(annual_recharge_volume, source_water_volume):
    # 
    if annual_recharge_volume is None:
        return None # irrelevant for confined aquifer
    return 100.0*annual_recharge_volume / np.sum(source_water_volume)


def compute_confined_storage_volume(confined, strat_df, Hmax, injection_wells_result, source_water_volume):  
    # annual injection volume``  
    # we assume the table has four overburden layer, layers 2 bedrock and 1 aquifer in the middle
    # todo: test
    if confined:        
        if len(strat_df) != 4:
            raise ValueError("Stratigraphy table must have four layers for confined aquifer")
        
        kaq = strat_df.iloc[2]["K"]
        B = strat_df.iloc[2]["thickness"]
        Ss = strat_df.iloc[2]["sy/ss"]
        transmissivity = kaq * B
        Ss = Ss * B      

        if injection_wells_result["number_of_wells"] == 1:
            max_injection_rate = injection_wells_result['number_of_wells'] * theis_drawdown_or_Q(Q_or_dh=Hmax, T=transmissivity, S=Ss, r=1, t=50, compute_Q=True)
        else:
            Q_per_well = np.max(source_water_volume)/30.25/injection_wells_result["number_of_wells"]
            dh_from_well_at_300ft = theis_drawdown_or_Q(Q_or_dh=Q_per_well, T=transmissivity, S=Ss, r=300, t=50, compute_Q=False)
            dh_superimposed = (Hmax/injection_wells_result["number_of_wells"]) + (dh_from_well_at_300ft * (injection_wells_result["number_of_wells"] -1))
            max_injection_rate = theis_drawdown_or_Q(Q_or_dh=dh_superimposed, T=transmissivity, S=Ss, r=1, t=50, compute_Q=True)
         
        
        return max_injection_rate * 365.25
    else:
        return None

def compute_confined_rechargability(annual_confined_storage_volume, source_water_volume):
    if annual_confined_storage_volume is None:
        return None # irrelevant for confined aquifer
    
    percentage = 100.0*annual_confined_storage_volume / np.sum(source_water_volume)
    if percentage > 100.0:
        return 100.0
    else:
        return percentage

def compute_leakage_significance(rechargability, strat_df):
    if rechargability is None:
        return None # irrelevant for unconfined aquifer
    
    top_confined_layer_k = strat_df.iloc[1]["K"]
    top_confined_layer_thickness = strat_df.iloc[1]["thickness"]
    bottom_confined_layer_k = strat_df.iloc[3]["K"]
    bottom_confined_layer_thickness = strat_df.iloc[3]["thickness"]

    leakance_top =  top_confined_layer_k/top_confined_layer_thickness
    leakance_bottom =  bottom_confined_layer_k/bottom_confined_layer_thickness
    leakance = max(leakance_top, leakance_bottom)

    k_aquifer = strat_df.iloc[2]["K"]
    aquifer_thickness = strat_df.iloc[2]["thickness"]
    transmissivity = k_aquifer * aquifer_thickness

    BB = np.sqrt(transmissivity / leakance)
    leakage_significance = BB/defaults['leakage_radius']
    if leakage_significance> 20.0:
        return "low"
    elif leakage_significance<20.0 and leakage_significance>1:
        return "medium"
    else:
        return "high"


def compute_depth_significance(confined, strat_df):
    if not (confined):
        return None # irrelevant for unconfined aquifer

    aquifer_depth = strat_df.iloc[0:2]["thickness"] 
    aquifer_depth = aquifer_depth.sum()

    if aquifer_depth > defaults['excessive_deep_aquifer'][1]:
        return "Too Deep"
    elif aquifer_depth > defaults['excessive_deep_aquifer'][0] and aquifer_depth <= defaults['excessive_deep_aquifer'][1]:
        return "Moderate Deep"
    else:
        return "Low Depth"

def compute_gs_slope_significance(unconfined, gs_slope):
    if not (unconfined):
        return None # irrelevant for confined aquifer
    if gs_slope < 2.0:
        return "Gentle"
    elif gs_slope >= 2.0 and gs_slope < 5.0:
        return "Moderate"
    else:
        return "Steep"
    

def compute_surface_recharge_suitability(gs_slope_significance, inflitration_significance, rechargability, remediate):
    surface_recharge_suitability = True
    if (inflitration_significance is None) or (not inflitration_significance):
        surface_recharge_suitability = False
        return surface_recharge_suitability
        
    if gs_slope_significance is None or not (gs_slope_significance in ["Gentle", "Moderate"]):
        surface_recharge_suitability = False
        return surface_recharge_suitability
    
    if rechargability < defaults["maximum_rechargability"]:
        surface_recharge_suitability = False
        return surface_recharge_suitability
    
    if not (remediate): # this is vadose zone remediation
        surface_recharge_suitability = False

    return surface_recharge_suitability
    
def get_stratigraphy_table(stratigraphy_table):
    """    
    Convert the stratigraphy table to a pandas DataFrame.
    Parameters:
    - stratigraphy_table: Input stratigraphy table (list of lists)
    Returns:
    - stratigraphy_table: pandas DataFrame
    """
    columns = ["thickness", "K", "sy/ss"]
    if isinstance(stratigraphy_table, list):
        if not all(len(row) == 3 for row in stratigraphy_table):
            raise ValueError("Each row in stratigraphy table must contain exactly 3 columns (thickness, K, sy/ss).")
        return pd.DataFrame(stratigraphy_table, columns=columns)
    else:
        raise ValueError("Invalid stratigraphy table format. Must be list of lists.")
  