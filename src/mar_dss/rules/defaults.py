
defaults = {}
defaults["k_min_vadose_threshold"] = 0.3
defaults['leakage_radius'] = 1000
defaults['excessive_deep_aquifer'] = [1500.0, 3000.0]

# maximum perecenatge of source water that can be recharged
defaults["maximum_rechargability"] = 50
defaults["max_injection_Q_per_well"] = 100000 #  ft^3/day
defaults["max_number_of_injection_wells"] = 20

#dary well 
defaults["max_dry_well_infiltration_rate_in_per_hr"] = 60000 #  ft^3/day
defaults["max_dry_well_transfer_rate_gpm"] = 50
defaults["max_drywell_depth_ft"] = 10


# default effective porosity for vadose zone (if not available from stratigraphy)
defaults["vadose_effective_porosity"] = 0.2 # porosity times moisture content
defaults["average_moisture_content"] = 0.1 # dimensionless

# minimum residence time for natural attenuation (days)
defaults["pathogenic_bacteria_residence_time"] = 30  # days - minimum for biodegradation
defaults["organic_matter_residence_time"] = 7 
defaults["trace_organic_matter_residence_time"] = 30
defaults["Nutrients_residence_time"] = 30



 # days - optimal for biodegradation