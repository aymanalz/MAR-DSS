import numpy as np
import pandas as pd
try:
    from mar_dss.rules.analytical_solutions import compute_recharge_rate
except ImportError:
    # Fallback for when running from source directory
    try:
        from src.mar_dss.rules.analytical_solutions import compute_recharge_rate
    except ImportError:
        # If both fail, define a placeholder
        def compute_recharge_rate(*args, **kwargs):
            raise NotImplementedError("compute_recharge_rate not available")


defaults = {"k_min_vadose_threshold": 0.3}


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
        raise ValueError("Confined aquifer: limiting layer is the upper confining layer.")

def find_min_k_vadose_zone(strat_df, limiting_layer):
    return strat_df.iloc[limiting_layer]["K"]

def check_topsoil_limiting(limiting_layer, k_min_vadose):
    if limiting_layer == 0 and k_min_vadose < defaults["k_min_vadose_threshold"]:
        return True 
    else:
        return False

def compute_min_gw_depth(limiting_layer, strat_df, d_gw_min):
   
    
    d_gw_min = float(d_gw_min)    
    limiting_layer = int(limiting_layer)
    k_min_vadose = strat_df.iloc[limiting_layer]["K"]
    if k_min_vadose >= defaults["k_min_vadose_threshold"]:        
        return d_gw_min
    else:
        layer_bottom_depth = strat_df["thickness"].cumsum()
        limiting_layer_bottom_depth = layer_bottom_depth.iloc[limiting_layer]
        return max(d_gw_min, limiting_layer_bottom_depth)



def compute_spread_area(k_min_vadose, max_available_area, gw_depth, source_water_volume, strat_df, limiting_layer, op_gw_depth):

    
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
    spread_area = np.mean(source_water_volume) / (k_min_vadose)
    
    # Iterative calculation to find appropriate spread area
    max_iterations = 100  # Safety limit
    iteration = 0
    while iteration < max_iterations:
        infl_rate = compute_recharge_rate(x=0, y=0,
                                         t=t, del_h=dh,
                                         spread_area=spread_area,
                                         k=k_mean,
                                         b=saturated_thickness, 
                                         sy=sy_mean)

        if infl_rate < k_min_vadose:
            spread_area = spread_area * infl_rate/k_min_vadose
        else:
            # If spread area is too large, reduce it
            spread_area = spread_area * k_min_vadose/ infl_rate # Reduce by 10% each iteration
        iteration += 1

        if abs(infl_rate - k_min_vadose) < 1e-5:
            break
    
    # Ensure we don't exceed max available area
    spread_area = min(spread_area, max_available_area)
    
    return {"spread_area": spread_area, "infl_rate": infl_rate, "inf_k_ratio": infl_rate/k_min_vadose}

def compute_optimal_vadose_storage(design_sizing_result):
    spread_area = design_sizing_result["spread_area"]
    infl_rate = design_sizing_result["infl_rate"]
    inf_k_ratio = design_sizing_result["inf_k_ratio"]
    return spread_area * infl_rate

# write a function that compute the available storage in an aquifer
def compute_available_storage(Dgw, Dgw_min, Aqtype, Ss, Hmax):
    """
    Compute the available storage in an aquifer.

    Parameters:
    - Dgw_min: Minimum depth to groundwater (float)
    - Dgw: Depth to groundwater (float)
    - Aqtype: Aquifer type (str), e.g., "unconfined" or "confined"
    - Ss: Specific storage (float)
    - Hmax: Maximum allowable head change (float)
    Returns:
    - available_storage: Available storage (float)
    """

    current_moisture_content = 0.0  # todo: find a way to estimate this.

    if Aqtype is None:
        raise ValueError(
            "Aqtype (aquifer type) must be specified as 'unconfined' or 'confined'."
        )

    if isinstance(Aqtype, str):
        aqtype = Aqtype.strip().lower()
    else:
        aqtype = str(Aqtype).strip().lower()

    if aqtype == "unconfined":
        if Ss is None or Dgw is None:
            raise ValueError(
                "Both Ss and Dgw must be provided for unconfined aquifer."
            )
        if Dgw < Dgw_min:
            return 0.0
        if current_moisture_content > Ss:
            return 0.0
        else:
            return (Ss - current_moisture_content) * (Dgw - Dgw_min)
    elif aqtype == "confined":
        if Ss is None:
            raise ValueError(
                "Ss (storage coefficient) must be provided for confined aquifer."
            )
        return Ss * Hmax
    else:
        raise ValueError(f"Unknown aquifer type: {Aqtype}")

def compute_infiltration_rate(Ks, UnSatClay, UnSatClayDepth):
    """
    Compute the infiltration rate of the aquifer.
    """
    if UnSatClay:
        return Ks * (1 - UnSatClayDepth)
    else:
        return Ks

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
  