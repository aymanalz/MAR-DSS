
defaults = {}
defaults["k_min_vadose_threshold"] = 0.3
defaults['leakage_radius'] = 1000
defaults['excessive_deep_aquifer'] = [1500.0, 3000.0]

# maximum perecenatge of source water that can be recharged
defaults["maximum_rechargability"] = 0

# default effective porosity for vadose zone (if not available from stratigraphy)
defaults["vadose_effective_porosity"] = 0.2 # porosity times moisture content
defaults["average_moisture_content"] = 0.1 # dimensionless

# minimum residence time for natural attenuation (days)
defaults["pathogenic_bacteria_residence_time"] = 30  # days - minimum for biodegradation
defaults["organic_matter_residence_time"] = 7 
defaults["trace_organic_matter_residence_time"] = 30
defaults["Nutrients_residence_time"] = 30

 # days - optimal for biodegradation