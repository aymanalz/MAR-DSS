import pandas as pd
from typing import Optional
import numpy as np
from mar_dss.rules.defaults import defaults
import mar_dss.app.utils.data_storage as dash_storage


# default_engineering_elements = {
#    "Flow Capture Structure": True,
#    "Rough Grading/Grubbing in Field":True,
  

#    "Sediment Removal Pond":True, #
#    "Conveyance to Sediment Removal Pond":"Trapezoidal Channel", # "Gravity Conveyance Pipeline" or "Pumped Conveyance"
#    "Sediment Removal Target":"Medium Silt", # "Medium Silt" or ""Fine Silt"
#    "Contaminant Filters":False, # 

#    "Storage Pond":True, #
#    "Pipeline to Storage Pond":True, #
#    "Pump to Storage Pond":True, #
#    "Controls for Storage Pond":True, #
#    "Electrical System for Storage Pond":True, #

#    "Pipeline to Infiltration Site":True, #
#    "Pump to Infiltration Site":True, #
#    "Controls for Infiltration Site":True, #
#    "Electrical System for Infiltration Site":True, #

#    "Dry Wells Infiltration":"None", # "Dry Wells Infiltration" or "None"
#    "Injection Wells Infiltration":"None", # "Injection Wells Infiltration" or "None"
#    "Infiltration Basin":"None", # "Infiltration Basin" or "None"  
   
# }

class CostCalculator:
    def __init__(
        self,        
        water_source: Optional[str] = None,
        storm_design_depth: Optional[float] = None,
        drainage_basin_area_acres: Optional[float] = None,
        total_storm_volume_af: Optional[float] = None, # likely not 
        basin_soil_type_infiltration_rate_in_per_hr: Optional[float] = None,
        percentage_storm_volume_to_capture: Optional[float] = None,
        total_runoff_volume_ft3: Optional[float] = None,
        distance_collection_to_sediment_pond_ft: Optional[float] = None,
        distance_sediment_to_storage_pond_ft: Optional[float] = None,
        sediment_pond_area_available_acres: Optional[float] = None,
        fine_sediment_removal_goal: Optional[str] = None,
        dry_well_infiltration_rate_in_per_hr: Optional[float] = None,
        dry_well_transfer_rate_gpm: Optional[float] = None,
        number_of_injection_wells: Optional[int] = None,
        injection_well_transfer_rate_gpm: Optional[float] = None,
        dry_well_diameter_ft: Optional[float] = None,
        collection_to_sediment_removal__conveyance_method: Optional[str] = None,
        recharge_method: Optional[str] = None,
        number_of_dry_wells: Optional[int] = None,
        dry_well_Q_ft3_per_day: Optional[float] = None,

    ):
        """Initialize MAR Cost Calculator with project parameters."""
        if water_source is not None:
            water_source_lower = water_source.lower()
            if water_source_lower == "stormwater":
                self.storm_design_depth = storm_design_depth
                self.drainage_basin_area_acres = (
                    drainage_basin_area_acres
                )
                self.total_storm_volume_af = total_runoff_volume_ft3/43560.0
                # todo: not used, remove if not needed
                self.basin_soil_type_infiltration_rate_in_per_hr = (
                    basin_soil_type_infiltration_rate_in_per_hr
                )
                self.percentage_storm_volume_to_capture = (
                    percentage_storm_volume_to_capture
                )
                self.total_runoff_volume_ft3 = total_runoff_volume_ft3
            elif water_source_lower == "treated_wastewater":
                pass
            elif water_source_lower == "brackish_water":
                pass
            else:
                raise ValueError(
                    f"Invalid water source: {water_source}. "
                    f"Valid options: 'stormwater', "
                    f"'treated_wastewater', 'brackish_water'"
                )

        self.water_source = water_source
        if fine_sediment_removal_goal in ["Fine Silt", "Medium Silt"]:
            self.sediment_type = fine_sediment_removal_goal
        else:
            raise ValueError(
                f"Invalid fine_sediment_removal_goal: "
                f"{fine_sediment_removal_goal}."
            )

        self.distance_collection_to_sediment_pond_ft = (
            distance_collection_to_sediment_pond_ft
        )
        self.distance_sediment_to_storage_pond_ft = (
            distance_sediment_to_storage_pond_ft
        )
        if collection_to_sediment_removal__conveyance_method in [
            "trapezoidal", "pipeline", "pumped"
        ]:
            self.collection_to_sediment_removal__conveyance_method = (
                collection_to_sediment_removal__conveyance_method
            )
        else:
            raise ValueError(
                f"Invalid "
                f"collection_to_sediment_removal__conveyance_method: "
                f"{collection_to_sediment_removal__conveyance_method}. "
                f"Valid options: 'trapezoidal', 'pumped', 'pipeline'"
            )

        self.sediment_pond_area_available_acres = (
            sediment_pond_area_available_acres
        )

        feasible_options = [
            "Fine Silt", "Medium Silt", "Coarse Silt", "Sand"
        ]
        if fine_sediment_removal_goal is not None:
            if fine_sediment_removal_goal not in feasible_options:
                raise ValueError(
                    f"Invalid fine_sediment_removal_goal: "
                    f"{fine_sediment_removal_goal}. "
                    f"Feasible options are: "
                    f"{', '.join(feasible_options)}"
                )
        self.fine_sediment_removal_goal = fine_sediment_removal_goal

        self.dry_well_diameter_ft = dry_well_diameter_ft
        self.dry_well_infiltration_rate_in_per_hr = (
            dry_well_infiltration_rate_in_per_hr
        )
        self.dry_well_transfer_rate_gpm = dry_well_transfer_rate_gpm
        self.injection_well_transfer_rate_gpm = (
            injection_well_transfer_rate_gpm
        )
        self.number_of_injection_wells = number_of_injection_wells
        self.number_of_dry_wells = number_of_dry_wells
        self.dry_well_Q_ft3_per_day = dry_well_Q_ft3_per_day

        if recharge_method in [
            "dry_well", "injection_well", "infiltration_basin"
        ]:
            self.recharge_method = recharge_method
        else:
            raise ValueError(
                f"Invalid recharge_method: {recharge_method}. "
                f"Valid options: 'dry_well', 'injection_well', "
                f"'infiltration_basin'"
            )

    def calculate_cost(self):
        #self.read_engineering_elements()
        self.hydro_calculations()
        self.conveyance_calculations()
        self.sediment_removal_pond()
        self.pump_conveyance_to_sediment_removal_pond()
        self.burried_pipeline_cost()
        self.storgae_pond()
        self.dry_wells_infiltration()
        self.injection_wells_infiltration()
        self.infiltration_basin()
        self.capital_costs()
        self.maintenance_costs()
        self.net_present_value()
    
    # def read_engineering_elements(self):
    #     # todo: read from data storage
    #     self.engineering_elements = default_engineering_elements


    def hydro_calculations(self):
        class Hydro:
            pass
        hydro = Hydro()
        hydro.basin_area_acres = self.drainage_basin_area_acres
        hydro.basin_area_ft2 = (
            self.drainage_basin_area_acres * 43560
        )      

        peak_flow_rate_ft3_per_hour = self.total_runoff_volume_ft3/12.0
        self.peak_flow_rate_gpm = peak_flow_rate_ft3_per_hour * 0.124675
        hydro.total_storm_volume_gals = (
            self.total_storm_volume_af * 325851.43
        )        
       
        # assuming triangular unit hydrograph, height is h and base 24 hours
        # the peak flow if total runoff volume is V
        
        self.hydro = hydro

    def conveyance_calculations(self):
        class Conveyance:
            pass

        conveyance = Conveyance()

        conveyance.culvert_size_table = [
            {
                "size_inches": 6, "area_ft2": 0.343,
                "flow_capacity_gpm": 153.9, "velocity_fps": 1.75
            },
            {
                "size_inches": 12, "area_ft2": 1.821,
                "flow_capacity_gpm": 817.3, "velocity_fps": 2.32
            },
            {
                "size_inches": 18, "area_ft2": 5.087,
                "flow_capacity_gpm": 2283.2, "velocity_fps": 2.88
            },
            {
                "size_inches": 24, "area_ft2": 10.959,
                "flow_capacity_gpm": 4918.7, "velocity_fps": 3.49
            },
            {
                "size_inches": 36, "area_ft2": 32.358,
                "flow_capacity_gpm": 14523.2, "velocity_fps": 4.58
            },
            {
                "size_inches": 48, "area_ft2": 69.708,
                "flow_capacity_gpm": 31287.0, "velocity_fps": 5.55
            },
            {
                "size_inches": 60, "area_ft2": 126.385,
                "flow_capacity_gpm": 56725.4, "velocity_fps": 6.44
            },
            {
                "size_inches": 72, "area_ft2": 205.45,
                "flow_capacity_gpm": 92212.1, "velocity_fps": 7.27
            },
        ]

        conveyance.trapezoidal_channel_table = [
            {
                "bottom_width_ft": None, "depth_ft": 0.5,
                "flowrate_cfs": 1.03, "flowrate_gpm": 462,
                "cost_per_foot": 5
            },
            {
                "bottom_width_ft": None, "depth_ft": 1,
                "flowrate_cfs": 6.56, "flowrate_gpm": 2944,
                "cost_per_foot": 32
            },
            {
                "bottom_width_ft": 3, "depth_ft": 1.5,
                "flowrate_cfs": 19.33, "flowrate_gpm": 8675,
                "cost_per_foot": 93
            },
            {
                "bottom_width_ft": 4, "depth_ft": 2,
                "flowrate_cfs": 41.64, "flowrate_gpm": 18688,
                "cost_per_foot": 200
            },
            {
                "bottom_width_ft": 6, "depth_ft": 3,
                "flowrate_cfs": 122.76, "flowrate_gpm": 55095,
                "cost_per_foot": 590
            },
            {
                "bottom_width_ft": 8, "depth_ft": 4,
                "flowrate_cfs": 264.38, "flowrate_gpm": 118654,
                "cost_per_foot": 1270
            },
            {
                "bottom_width_ft": 9, "depth_ft": 4.5,
                "flowrate_cfs": 361.94, "flowrate_gpm": 162439,
                "cost_per_foot": 1738
            },
            {
                "bottom_width_ft": 10, "depth_ft": 5,
                "flowrate_cfs": 479.35, "flowrate_gpm": 215132,
                "cost_per_foot": 2302
            },
        ]

        conveyance.culvert_size_table = pd.DataFrame(
            conveyance.culvert_size_table
        )
        culvert_cost = [115, 185, 265, 350, 525, 800, 1100, 1450]
        conveyance.culvert_size_table['cost_per_foot'] = culvert_cost
        conveyance.trapezoidal_channel_table = pd.DataFrame(
            conveyance.trapezoidal_channel_table
        )

        conveyance.culvert_size_table = (
            conveyance.culvert_size_table[
                conveyance.culvert_size_table["flow_capacity_gpm"] >=
                self.peak_flow_rate_gpm
            ].iloc[0]
        )
        conveyance.trapezoidal_channel_table = (
            conveyance.trapezoidal_channel_table[
                conveyance.trapezoidal_channel_table["flowrate_gpm"] >=
                self.peak_flow_rate_gpm
            ].iloc[0]
        )
        self.conveyance = conveyance

    def sediment_removal_pond(self):
        class SedimentRemovalPond:
            pass
        df = pd.DataFrame(
            columns=["Fine Silt", "Medium Silt"],
            index=[
                "Peak Storm Flow Rate (gpm)",
                "Channel Water Depth/Pond Depth (ft)",
                "Target Particle Size (mm)",
                "Required residence time for 0.4 inch Fall ((in/min)",
                "Number of 0.4in Falls in Depth",
                "Total time for total pond depth (min)",
                "Required sediment trap volume (gal)",
                "Required sediment trap volume (cf)",
                "Sediment Trap Water Depth",
                "Sediment Trap Footprint (sf)",
                "Sediment Trap Footprint (ac)",
                "Side length of square trap (ft)"
            ]
        )

        df.loc["Peak Storm Flow Rate (gpm)"] = self.peak_flow_rate_gpm
        df.loc["Channel Water Depth/Pond Depth (ft)"] = 36
        df.loc["Target Particle Size (mm)"] = [0.01, 0.03]
        df.loc["Required residence time for 0.4 inch Fall ((in/min)"] = (
            [3.4, 0.38]
        )
        df.loc["Number of 0.4in Falls in Depth"] = 90
        df.loc["Total time for total pond depth (min)"] = (
            [90 * 3.4, 90 * 0.38]
        )
        df.loc["Required sediment trap volume (gal)"] = (
            df.loc["Total time for total pond depth (min)"] *
            self.peak_flow_rate_gpm
        )
        df.loc["Required sediment trap volume (cf)"] = (
            df.loc["Required sediment trap volume (gal)"] / 7.48
        )
        df.loc["Sediment Trap Water Depth (ft)"] = 3
        df.loc["Sediment Trap Footprint (sf)"] = (
            df.loc["Required sediment trap volume (cf)"] /
            df.loc["Sediment Trap Water Depth (ft)"]
        )
        df.loc["Sediment Trap Footprint (ac)"] = (
            df.loc["Sediment Trap Footprint (sf)"] / 43560
        )
        df.loc["Side length of square trap (ft)"] = np.sqrt(
            df.loc["Sediment Trap Footprint (sf)"].astype(float)
        )

        self.sediment_removal_pond_calculations = df
        self.sediment_removal_pond_area_acres = (
            df.loc["Sediment Trap Footprint (ac)"][self.sediment_type]
        )

    def contaminant_filters(self):
        """Cartridge Flow Rate and Requirements by Diameter."""
        cartridge_df = pd.DataFrame({
            "12-inch Diameter": [5.0, 0.0, 0],
            "18-inch Diameter": [7.5, 0.0, 0],
            "27-inch Diameter": [11.3, 0.0, 0]
        }, index=[
            "Cartridge Flow Rate (gpm)",
            "Reduced Peak Flowrate (gpm)",
            "Number of Cartridges Required"
        ])

        cartridge_df.loc["Reduced Peak Flowrate (gpm)"] = (
            self.peak_flow_rate_gpm * 0.12
        )
        cartridge_df.loc["Number of Cartridges Required"] = (
            cartridge_df.loc["Reduced Peak Flowrate (gpm)"] /
            cartridge_df.loc["Cartridge Flow Rate (gpm)"]
        )
        cartridge_df.loc["Number of Cartridges Required"] = np.ceil(
            cartridge_df.loc["Number of Cartridges Required"]
        )

        self.cartridge_df = cartridge_df

    def pump_conveyance_to_sediment_removal_pond(self):
        Q = self.peak_flow_rate_gpm * 0.002228009
        velocity = 5
        area = Q / velocity
        diameter = 2 * np.sqrt(area / np.pi)

        class Pump:
            pass
        pump = Pump()
        pump.diameter_inches = diameter * 12
        pump.velocity = velocity

        self.pump_to_storage_pond = pump

    def burried_pipeline_cost(self):
        """Pipe diameter lookup table based on design flow rate (gpm)."""
        pipe_diameter_df = pd.DataFrame({
            "Design gpm": [
                500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000,
                9000, 10000, 11000
            ],
            "Diameter": [6, 10, 14, 16, 20, 20, 24, 24, 24, 30, 30, 30]
        })

        pipe_diameter_df['$ per foot'] = (
            pipe_diameter_df['Diameter'] * 3.6
        )

        mask = (
            pipe_diameter_df['Diameter'] >=
            self.pump_to_storage_pond.diameter_inches
        )
        pipe_diameter_df = pipe_diameter_df[mask].iloc[0]
        self.pipe_to_storage_pond = pipe_diameter_df

    def storgae_pond(self):
        class StoragePond:
            pass
        storage_pond = StoragePond()

        storm_volume = self.hydro.total_storm_volume_gals
        storage_pond.depth_ft = 5
        storage_pond.freeboard_ft = 2
        storage_pond.volume_ft3 = storm_volume * 0.133681
        storage_pond.area_ft2 = (
            storage_pond.volume_ft3 / storage_pond.depth_ft
        )
        storage_pond.side_length_ft = np.sqrt(storage_pond.area_ft2)
        storage_pond.area_acres = storage_pond.area_ft2 / 43560.0

        self.storage_pond = storage_pond

    def dry_wells_infiltration(self):
        df = pd.DataFrame(columns=["Well Diameter (ft)"])
        df["Well Diameter (ft)"] = [4, 5, 6]
        df['Well Depth (ft)'] = [103, 104, 105]
        df['Well Volume (ft3)'] = (
            df['Well Depth (ft)'] * (df['Well Diameter (ft)']**2) *
            np.pi / 4
        )
        side_area = (
            2 * np.pi * df['Well Diameter (ft)'] / 2 * 3.0
        )
        df['Well Surface Area (ft2)'] = (
            df['Well Diameter (ft)'] * np.pi *
            df['Well Diameter (ft)'] / 4.0
        )
        df['Well Surface Area (in2)'] = (
            df['Well Surface Area (ft2)'] * 144.0
        )

        infil_rate_in_per_hr = self.dry_well_infiltration_rate_in_per_hr
        df['Well Capacity (in3/hr)'] = (
            df['Well Surface Area (in2)'] * infil_rate_in_per_hr
        )
        df['Well Capacity (gal/hr)'] = (
            df['Well Capacity (in3/hr)'] / 231.0
        )
        df['Well Capacity (gpm)'] = (
            df['Well Capacity (gal/hr)'] / 60.0
        )

        df['Number of Wells Required'] = np.ceil(
            self.dry_well_transfer_rate_gpm / df['Well Capacity (gpm)']
        )
        df['Infiltration Rate (gal/day)'] = (
            df['Well Capacity (gpm)'] *
            df['Number of Wells Required'] * 24 * 60
        )

        df['Time to Drain (days)'] = (
            self.hydro.total_storm_volume_gals /
            df['Infiltration Rate (gal/day)']
        )

        self.dry_wells_infiltration_calculations = df

    def injection_wells_infiltration(self):
        df = pd.DataFrame(columns=[
            "Transfer Rate (gpm)", "Number of Injection Wells",
            "Total Transfer Rate (gpm)", "Time to Drain (days)"
        ])

        df.loc["Transfer Rate (gpm)"] = (
            self.injection_well_transfer_rate_gpm
        )
        df.loc["Number of Injection Wells"] = (
            self.number_of_injection_wells
        )
        df.loc["Total Transfer Rate (gpm)"] = (
            df.loc["Transfer Rate (gpm)"] *
            df.loc["Number of Injection Wells"]
        )
        df.loc["Time to Drain (days)"] = (
            self.hydro.total_storm_volume_gals /
            df.loc["Total Transfer Rate (gpm)"] / 24 / 60
        )
        self.injection_wells_infiltration_calculations = df

    def infiltration_basin(self):
        df = pd.DataFrame(index=[0])
        df.loc[0, 'Basin Depth (ft)'] = 5
        df.loc[0, 'Basin Area (sf)'] = (
            self.hydro.total_storm_volume_gals * 0.133681 /
            df.loc[0, 'Basin Depth (ft)']
        )
        df.loc[0, 'Side Length (ft)'] = np.sqrt(
            df.loc[0, 'Basin Area (sf)']
        )
        df.loc[0, 'infil_rate (in/hr)'] = (
            self.basin_soil_type_infiltration_rate_in_per_hr
        )
        df.loc[0, 'Time to Drain (days)'] = (
            (df.loc[0, 'Basin Depth (ft)'] * 12) /
            (df.loc[0, 'infil_rate (in/hr)'] * 24)
        )
        self.infiltration_basin_calculations = df

    def capital_costs(self):
        columns = [
            'Category', 'Item', 'Unit', 'Unit Cost $', 'Number of Units'
        ]
        df = pd.DataFrame(columns=columns)        

        # ======== collection point and site preparation ========
        irow = 0
        flow_capture_values = dash_storage.get_data("flow_capture_values")
        if "rough_grading" in flow_capture_values:
            unit_price =1500
        else:
            unit_price = 0       
        df.loc[irow] = [
            'COLLECTION BASIN PREPARATION',
            'Rough Grading/Grubbing in Field', 'acres', unit_price,
            self.hydro.basin_area_acres
        ]

        # ======== flow capture structure ========
        irow += 1
        if "flow_capture_structure" in flow_capture_values:
            unit_price = 10000
        else:
            unit_price = 0
        df.loc[irow] = [
            'COLLECTION BASIN PREPARATION', 'Flow Capture Structure',
            'LS', unit_price, 1.0
        ]
        
        # ======== pump is used to divert water ========
        irow += 1
        if "pump_used" in flow_capture_values:
            unit_price = 50000
        else:
            unit_price = 0
        df.loc[irow] = [
            'COLLECTION BASIN PREPARATION', 'Pump', 'LF', unit_price, 1.0
        ]
      

        # ======== conveyance to sediment removal pond ======== 
        conveyance_method = dash_storage.get_data("conveyance_method")
      
        irow += 1
        if ("trapezoidal" == conveyance_method):
            df.loc[irow] = [
                'CONVEYANCE TO SEDIMENT POND',
                'Trapezoidal Channel', 'LF', 93,
                self.distance_collection_to_sediment_pond_ft
            ]
        elif ("pipeline" == conveyance_method):
            df.loc[irow] = [
                'CONVEYANCE TO SEDIMENT POND', 'Pipeline', 'LF', 72,
                self.distance_collection_to_sediment_pond_ft
            ]
        elif ("pumped" == conveyance_method):
            df.loc[irow] = [
                'CONVEYANCE TO SEDIMENT POND',
                'Pumped Conveyance', 'LF', 400,
                self.distance_collection_to_sediment_pond_ft
            ]
        
        # ======== sediment removal pond ========
        remove_sediment = dash_storage.get_data("remove_sediment_removal_pond")
        if remove_sediment is None:
            remove_sediment = False

        if remove_sediment:
            unit_price = 0
        else:
            unit_price = 10000
        irow += 1
        df.loc[irow] = [
            'SEDIMENT REMOVAL POND', 'Trash Rack', 'LS', unit_price, 1
        ]
       
        if not(remove_sediment):
            unit_price = 0
        else:
            unit_price = 500000
        pond_area = self.sediment_removal_pond_area_acres
        irow += 1
        df.loc[irow] = [
            'SEDIMENT REMOVAL POND', self.sediment_type, 'Acre', unit_price,
            pond_area
        ]

        # ==== storage
        storage_pond_values = dash_storage.get_data("storage_pond_values")
        pumped_storage_values = dash_storage.get_data("pumped_storage_values")
        storage = "storage_pond_construction" in storage_pond_values

        if storage is None:
            storage = True
        # ======== pipeline to storage pond ========
        unit_price = 0
        if storage:
            if "pipeline_cost" in pumped_storage_values:
                unit_price = 72
   
        irow += 1
        df.loc[irow] = [
            'PUMPED CONVEYANCE TO STORAGE/INFILTRATION POND',
            'Pipeline Cost',
            'LF', unit_price, self.distance_sediment_to_storage_pond_ft
        ]
        # ======== pumping and bag filter cost for storage pond ========
        unit_price = 0        
        if storage:
            if "pumping_bag_filter_cost" in pumped_storage_values:
                unit_price = 100000
        irow += 1
        df.loc[irow] = [
            'PUMPED CONVEYANCE TO STORAGE/INFILTRATION POND',
            'Pumping and Bag Filter Cost', 'LS', unit_price, 1
        ]

        # ======== controls  ========
        unit_price = 0
        if storage:         
            if "controls" in pumped_storage_values:
                unit_price = 50000         
        
        irow += 1
        df.loc[irow] = [
            'PUMPED CONVEYANCE TO STORAGE/INFILTRATION POND',
            'Controls', 'LS', unit_price, 1
        ]
        # if self.engineering_elements["Electrical System for Storage Pond"] and storage:
        #     unit_price = 20000
        # else:
        # ======== electrical system for storage pond ========
        unit_price = 0
        if storage:
            if "electrical_system" in pumped_storage_values:
                unit_price = 20000
           
        irow += 1
        df.loc[irow] = [
            'PUMPED CONVEYANCE TO STORAGE/INFILTRATION POND',
            'Electrical System', 'LS', unit_price, 1
        ]

        if storage:
            unit_price = 200000
        else:
            unit_price = 0
        irow += 1
        df.loc[irow] = [
            'STORAGE POND', 'Pond construction cost', 'Acre', unit_price,
            self.storage_pond.area_ft2 / 43560.0
        ]

        # ==== infiltration site
        pumped_infiltration_values = dash_storage.get_data("pumped_infiltration_values")
        if "infiltration_pipeline_cost" in pumped_infiltration_values:
            unit_price = 72
        else:
            unit_price = 0

        irow += 1
        df.loc[irow] = [
            'PUMPED CONVEYANCE TO INFILTRATION SITE',
            'Pipeline Cost', 'LF', unit_price, 500
        ]
        if"infiltration_pumping_bag_filter_cost" in pumped_infiltration_values:
            unit_price = 100000
        else:
            unit_price = 0
        irow += 1
        df.loc[irow] = [
            'PUMPED CONVEYANCE TO INFILTRATION SITE',
            'Pumping and Bag Filter Cost', 'LS', unit_price, 1
        ]
        if "infiltration_controls" in pumped_infiltration_values:
            unit_price = 50000
        else:
            unit_price = 0
        irow += 1
        df.loc[irow] = [
            'PUMPED CONVEYANCE TO INFILTRATION SITE',
            'Controls', 'LS', unit_price, 1
        ]
        if"infiltration_electrical_system" in pumped_infiltration_values:
            unit_price = 20000
        else:
            unit_price = 0
        irow += 1
        df.loc[irow] = [
            'PUMPED CONVEYANCE TO INFILTRATION SITE',
            'Electrical System', 'LS', unit_price, 1
        ]

        mask = (
            self.dry_wells_infiltration_calculations['Well Diameter (ft)'] ==
            self.dry_well_diameter_ft
        )

        # unit_price = 0
        # if self.recharge_method == "dry_well":
        unit_price = 50000
        irow += 1
        irow_dry_well = irow
        if self.number_of_dry_wells is not None:
            df.loc[irow] = [
                'INFILTRATION', 'Dry Well Cost', 'LF', unit_price,
               self.number_of_dry_wells
            ]
        else:
            
            df.loc[irow] = [
                'INFILTRATION', 'Dry Well Cost', 'LF', unit_price,
                self.dry_wells_infiltration_calculations[mask][
                    "Number of Wells Required"
                ].values[0]
            ]
        unit_price = 250000
        irow += 1
        irow_injection_wells = irow
        df.loc[irow] = [
            'INFILTRATION', 'Injection Wells', 'EA', unit_price,
            self.number_of_injection_wells
        ]
       
        unit_price = 100000
        irow += 1
        irow_distribution_piping = irow
        df.loc[irow] = [
            'INFILTRATION', "Distribution Piping", "LS", unit_price, 1
        ]
        irow += 1
        irow_infiltration_basin = irow
        unit_price = 200000
        df.loc[irow] = [
            'INFILTRATION', "Infiltration Basin", "Acre", unit_price,
            self.infiltration_basin_calculations["Basin Area (sf)"][0] /
            43560.0
        ]

        for recharge_method in ["Spreading Pond", "Injection Wells", "Dry Wells"]:
            name = recharge_method + " Cost ($)"
            unit_price = 0
            if recharge_method == "Spreading Pond":
                unit_price = 200000
                df.loc[irow_dry_well,  'Unit Cost $'] = 0 # dru well
                df.loc[irow_injection_wells,  'Unit Cost $'] = 0 # injection wells
                df.loc[irow_distribution_piping,  'Unit Cost $'] = 0 # distribution piping
                df.loc[irow_infiltration_basin,  'Unit Cost $'] = unit_price # infiltration basin
            elif recharge_method == "Injection Wells":
                unit_price = 250000
                df.loc[irow_dry_well,  'Unit Cost $'] = 0 # dru well
                df.loc[irow_injection_wells,  'Unit Cost $'] = unit_price # injection wells
                df.loc[irow_distribution_piping,  'Unit Cost $'] = 100000 # distribution piping
                df.loc[irow_infiltration_basin,  'Unit Cost $'] = 0 # infiltration basin
            elif recharge_method == "Dry Wells":
                unit_price = 50000                 
                df.loc[irow_dry_well,  'Unit Cost $'] = unit_price # dry well
                df.loc[irow_injection_wells,  'Unit Cost $'] = 0 # injection wells
                df.loc[irow_distribution_piping,  'Unit Cost $'] = 100000 # distribution piping
                df.loc[irow_infiltration_basin,  'Unit Cost $'] = 0 # infiltration basin

            df[name] = (
                df['Unit Cost $'] * df['Number of Units']
            )
            subtotal = df[name].sum()
            df.loc['Subtotal', name] = subtotal
            df.loc['Project Management', name] = subtotal * 0.1
            df.loc['Permitting',name] = subtotal * 0.02
            df.loc['Legal Fees', name] = subtotal * 0.02
            df.loc['Engineering', name] = subtotal * 0.1
            df.loc['Construction Admin and Oversight',name] = (
                subtotal * 0.12
            )

            df.loc['subtotal_with_fees',name] = (
            df.loc['Subtotal',name] +
            df.loc['Project Management', name] +
            df.loc['Permitting', name] +
            df.loc['Legal Fees', name] +
            df.loc['Engineering', name] +
            df.loc['Construction Admin and Oversight', name]
            )
            df.loc['Contingency', name] = (
            df.loc['subtotal_with_fees', name] * 0.3
            )
            df.loc['Capital Total Cost', name] = (
            df.loc['subtotal_with_fees', name] +
            df.loc['Contingency', name]
             )

            



        # df.loc['subtotal_with_fees', 'Total Cost ($)'] = (
        #     df.loc['Subtotal', 'Total Cost ($)'] +
        #     df.loc['Project Management', 'Total Cost ($)'] +
        #     df.loc['Permitting', 'Total Cost ($)'] +
        #     df.loc['Legal Fees', 'Total Cost ($)'] +
        #     df.loc['Engineering', 'Total Cost ($)'] +
        #     df.loc['Construction Admin and Oversight', 'Total Cost ($)']
        # )
        # df.loc['Contingency', 'Total Cost ($)'] = (
        #     df.loc['subtotal_with_fees', 'Total Cost ($)'] * 0.3
        # )
        # df.loc['Capital Total Cost', 'Total Cost ($)'] = (
        #     df.loc['subtotal_with_fees', 'Total Cost ($)'] +
        #     df.loc['Contingency', 'Total Cost ($)']
        # )
        self.capital_costs_calculations = df

    def maintenance_costs(self):
        columns = [
            'Category', 'Item', 'Unit', 'Unit Cost $', 'Number of Units'
        ]
        df = pd.DataFrame(columns=columns)
        df.loc[0] = [
            'COLLECTION BASIN', 'Rough Grading', 'LS', 5000, 1.0
        ]
        df.loc[1] = [
            'COLLECTION BASIN', 'Material Hauling', 'LS', 2000, 1.0
        ]
        df.loc[2] = [
            'COLLECTION BASIN', 'Flow Capture Structure', 'LS', 1000, 1.0
        ]

        unit_price = 0
        if (
            self.collection_to_sediment_removal__conveyance_method ==
            "trapezoidal"
        ):
            unit_price = 50.0
        df.loc[3] = [
            'CONVEYANCE TO SEDIMENT POND',
            'Trapezoidal Channel Maintenance', 'LF', unit_price,
            self.distance_collection_to_sediment_pond_ft
        ]

        unit_price = 0
        if (
            self.collection_to_sediment_removal__conveyance_method ==
            "pipeline"
        ):
            unit_price = 5
        df.loc[4] = [
            'CONVEYANCE TO SEDIMENT POND',
            'Gravity Conveyance Pipeline Maintenance', 'LF', unit_price,
            self.distance_collection_to_sediment_pond_ft
        ]
        unit_price = 0
        if (
            self.collection_to_sediment_removal__conveyance_method ==
            "pumped"
        ):
            unit_price = 2000

        df.loc[5] = [
            'CONVEYANCE TO SEDIMENT POND',
            'Pumped Conveyance Maintenance', 'LS', unit_price, 1
        ]

        df.loc[6] = [
            'SEDIMENT REMOVAL POND', 'Trash Rack Maintenance',
            'LS', 5000, 1
        ]
        df.loc[7] = [
            'SEDIMENT REMOVAL POND', 'Sediment Removal Maintenance',
            'Acre', 75000, self.sediment_removal_pond_area_acres
        ]

        df.loc[8] = [
            'PUMPED CONVEYANCE TO STORAGE/INFILTRATION POND',
            'Pipeline Maintenance', 'LS', 3000, 1
        ]
        df.loc[9] = [
            'PUMPED CONVEYANCE TO STORAGE/INFILTRATION POND',
            'Pump Maintenance', 'LS', 10000, 1
        ]
        df.loc[10] = [
            'PUMPED CONVEYANCE TO STORAGE/INFILTRATION POND',
            'Pumping and Bag Filter Cost', 'LS', 10000, 1
        ]
        df.loc[11] = [
            'PUMPED CONVEYANCE TO STORAGE/INFILTRATION POND',
            'Power', 'LS', 2000, 1
        ]

        df.loc[12] = [
            'STORAGE POND', 'Sediment Removal and Grading', 'Acre', 2500,
            self.storage_pond.area_ft2 / 43560.0
        ]

        df.loc[13] = [
            'PUMPED CONVEYANCE TO INFILTRATION SITE',
            'Pipeline Maintenance', 'LS', 1000, 1
        ]
        df.loc[14] = [
            'PUMPED CONVEYANCE TO INFILTRATION SITE',
            'Pump Maintenance', 'LS', 2500, 1
        ]
        df.loc[15] = [
            'PUMPED CONVEYANCE TO INFILTRATION SITE',
            'Pumping and Bag Filter Cost', 'LS', 10000, 1
        ]
        df.loc[16] = [
            'PUMPED CONVEYANCE TO INFILTRATION SITE',
            'Power', 'LS', 2000, 1
        ]

        mask = (
            self.dry_wells_infiltration_calculations['Well Diameter (ft)'] ==
            self.dry_well_diameter_ft
        )
        nwells = (
            self.dry_wells_infiltration_calculations[mask][
                "Number of Wells Required"
            ].values[0]
        )
        unit_price = 0
        if self.recharge_method == "dry_well":
            unit_price = 1000
        df.loc[17] = [
            'INFILTRATION', 'Dry Well Maintenance', 'EA', unit_price,
            nwells
        ]
        unit_price = 0
        if self.recharge_method == "injection_well":
            unit_price = 2000
        df.loc[18] = [
            'INFILTRATION', 'Injection Well Maintenance', 'EA', unit_price,
            self.number_of_injection_wells
        ]
        unit_price = 0
        if self.recharge_method in ["infiltration_basin"]:
            unit_price = 2000
        df.loc[19] = [
            'INFILTRATION', 'Injection Well Pumping and Bag Filter',
            'LS', unit_price, 1.0
        ]
        unit_price = 0
        if self.recharge_method in ["injection_well"]:
            unit_price = 1000
        df.loc[20] = [
            'INFILTRATION', 'Injection Well Power', 'LS', unit_price, 1
        ]
        unit_price = 0
        if self.recharge_method in ["infiltration_basin"]:
            unit_price = 2500
        df.loc[21] = [
            'INFILTRATION', 'Infiltration Basin Maintenance',
            'Acre', unit_price,
            self.infiltration_basin_calculations["Basin Area (sf)"][0] /
            43560.0
        ]
        for recharge_method in ["Spreading Pond", "Injection Wells", "Dry Wells"]:
            name = recharge_method + " Maintenance Cost ($)"
            unit_price = 0
            if recharge_method == "Spreading Pond":
               
                df.loc[17,  'Unit Cost $'] = 0 # DRY WELL
                df.loc[18,  'Unit Cost $'] = 0 # injection well maintenance
                df.loc[19,  'Unit Cost $'] = 0 # injection well pumping and bag filter
                df.loc[20,  'Unit Cost $'] = 0 # injection well power
                df.loc[21,  'Unit Cost $'] = 2500 # infiltration basin maintenance
            elif recharge_method == "Injection Wells":
                df.loc[17,  'Unit Cost $'] = 0 # DRY WELL
                df.loc[18,  'Unit Cost $'] = 2000 # injection well maintenance
                df.loc[19,  'Unit Cost $'] = 2000 # injection well pumping and bag filter
                df.loc[20,  'Unit Cost $'] = 1000 # injection well power
                df.loc[21,  'Unit Cost $'] = 0 # infiltration basin maintenance
            elif recharge_method == "Dry Wells":
                df.loc[17,  'Unit Cost $'] = 1000 # DRY WELL
                df.loc[18,  'Unit Cost $'] = 0 # injection well maintenance
                df.loc[19,  'Unit Cost $'] = 0 # injection well pumping and bag filter
                df.loc[20,  'Unit Cost $'] = 0 # injection well power
                df.loc[21,  'Unit Cost $'] = 0 # infiltration basin maintenance
            
            

            df[name] = (
                df['Unit Cost $'] * df['Number of Units']
            )

            subtotal = df[name].sum()
            df.loc['Subtotal Maintenance Cost ($)', name] = (
                subtotal
            )

            df.loc['Project Management', name] = (
                subtotal * 0.1
            )
            df.loc['Reporting', name] = (
                subtotal * 0.02
            )
            df.loc['Engineering', name] = (
                subtotal * 0.1
            )
            df.loc['Construction Admin and Oversight', name] = (
                subtotal * 0.12
            )
            df.loc['Subtotal with Admin Fees', name] = (
                subtotal +
                df.loc['Project Management', name] +
                df.loc['Reporting', name] +
                df.loc['Engineering', name] +
                df.loc['Construction Admin and Oversight', name]
            )
            df.loc['Contingency', name] = (
                df.loc['Subtotal with Admin Fees', name] * 0.3
            )
            df.loc['Annual Grand Maintenance Cost', name] = (
                df.loc['Subtotal with Admin Fees', name] +
                df.loc['Contingency', name]
            )

        self.maintenance_costs_calculations = df

    def net_present_value(self):
        df = pd.DataFrame()           
        df.index = range(1, 21)
        df.index.name = 'Year'
        for recharge_method in ["Spreading Pond", "Injection Wells", "Dry Wells"]:
            name1 = recharge_method + " Cost ($)"
            capital_cost = (
                self.capital_costs_calculations.loc[
                    'Capital Total Cost', name1
                ]
            )
            name2 = recharge_method + " Maintenance Cost ($)"

            annual_maintenance_cost = (
                self.maintenance_costs_calculations.loc[
                    'Annual Grand Maintenance Cost', name2
                ]
            )
            annual_esclation_rate = 2.99 / 100
            npv_discount_rate = 5.01 / 100

            inflation_adjusted_maintenance_cost = []
            pv_costs = 0
            net_value = []
            for i in range(1, 21):
                if i == 1:
                    inflation_adjusted_maintenance_cost.append(
                        annual_maintenance_cost
                    )
                    pv_costs = (
                        pv_costs +
                        (annual_maintenance_cost /
                        (1 + npv_discount_rate)**i)
                    )
                    net_value.append(pv_costs + capital_cost)
                    continue
                previous_cost = inflation_adjusted_maintenance_cost[i-2]
                current_cost = (
                    previous_cost + previous_cost * annual_esclation_rate
                )
                inflation_adjusted_maintenance_cost.append(current_cost)
                pv_costs = (
                    pv_costs + (current_cost / (1 + npv_discount_rate)**i)
                )
                net_value.append(pv_costs + capital_cost)
            pv_costs = pv_costs + capital_cost
            name3 = recharge_method + " Net Present Value ($)"
            df[name3] = net_value
        self.net_present_value_calculations = df


# if __name__ == "__main__":
#     cost_calculator = CostCalculator(
#         water_source="stormwater", storm_design_depth=1.8,
#         drainage_basin_area_acres=35,
#         total_storm_volume_af=6.52,
#         basin_soil_type_infiltration_rate_in_per_hr=0.2,
#         peak_flow_rate_gpm=3958,
#         fine_sediment_removal_goal="Fine Silt",
#         distance_collection_to_sediment_pond_ft=2640,
#         distance_sediment_to_storage_pond_ft=2640,
#         dry_well_infiltration_rate_in_per_hr=5,
#         dry_well_transfer_rate_gpm=50,
#         injection_well_transfer_rate_gpm=50,
#         number_of_injection_wells=5,
#         collection_to_sediment_removal__conveyance_method="trapezoidal",
#         dry_well_diameter_ft=6,
#         recharge_method="dry_well"
#     )
#     cost_calculator.calculate_cost()
