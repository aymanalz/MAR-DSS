
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


    current_moisture_content = 0.0 # todo: find a way to estimate this.
    
    if Aqtype is None:
        raise ValueError("Aqtype (aquifer type) must be specified as 'unconfined' or 'confined'.")

    if isinstance(Aqtype, str):
        aqtype = Aqtype.strip().lower()
    else:
        aqtype = str(Aqtype).strip().lower()

    if aqtype == "unconfined":        
        if Ss is None or Dgw is None:
            raise ValueError("Both Ss and Dgw must be provided for unconfined aquifer.")
        if Dgw < Dgw_min:
            return 0.0
        if current_moisture_content>Ss:
            return 0.0
        else:
            return (Ss-current_moisture_content) * (Dgw - Dgw_min)
    elif aqtype == "confined":
        if Ss is None:
            raise ValueError("Ss (storage coefficient) must be provided for confined aquifer.")
        return Ss * Hmax
    else:
        raise ValueError(f"Unknown aquifer type: {Aqtype}")

