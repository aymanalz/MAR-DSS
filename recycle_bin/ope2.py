import osmnx as ox
import folium  # New import for interactive mapping
import geopandas as gpd

# --- Configuration ---
# 1. Define the geographic area of interest
PLACE_NAME = "Oakland, California, USA"
OUTPUT_FILE = "waterways_map.html" # Name of the output HTML file

# 2. Define the OpenStreetMap tags for streams and rivers
# The key is 'waterway', and the values are 'stream' and 'river'
STREAM_TAGS = {"waterway": ["stream", "river", "canal"]}

# --- Data Fetching ---

print(f"Fetching OpenStreetMap data for streams in {PLACE_NAME}...")

try:
    # Use osmnx to download features based on the place name and tags.
    # The result is a GeoDataFrame containing all matching features.
    gdf_features = ox.features.features_from_place(PLACE_NAME, tags=STREAM_TAGS)
    print("Stream data download complete.")

    # Get the boundary of the place to determine the map center
    gdf_boundary = ox.geocode_to_gdf(PLACE_NAME)
    
except Exception as e:
    print(f"An error occurred during data fetching: {e}")
    print("Please check the location name and your internet connection.")
    exit()

# --- Data Processing and Filtering ---

# Filter the GeoDataFrame to keep only linear geometries (LineString/MultiLineString)
# These represent the actual flow path of the streams and rivers.
gdf_streams = gdf_features[
    gdf_features.geometry.geom_type.isin(['LineString', 'MultiLineString'])
].copy()

# Check if any stream data was found
if gdf_streams.empty:
    print(f"No stream or river data found for {PLACE_NAME} with the specified tags.")
    exit()

print(f"Found {len(gdf_streams)} linear waterway features.")

# --- Visualization (using Folium) ---

# 1. Determine the center point of the map
# We use the centroid of the area boundary for accurate centering
center_lat = gdf_boundary.geometry.centroid.y.mean()
center_lon = gdf_boundary.geometry.centroid.x.mean()

# 2. Create the Folium map object
m = folium.Map(
    location=[center_lat, center_lon], 
    zoom_start=12,
    tiles="cartodbpositron" # A clean, light basemap for better visibility
)

# 3. Add the streams/rivers to the map
# Folium GeoJson requires the GeoDataFrame to be converted to GeoJSON format
folium.GeoJson(
    gdf_streams.to_json(), # Convert GeoDataFrame to GeoJSON string
    name='OSM Streams and Rivers',
    style_function=lambda x: {
        'color': '#1E90FF', # Dodger Blue
        'weight': 3,
        'opacity': 0.9
    },
    # Add a tooltip to show the name of the waterway when hovered over
    tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Waterway Name:'])
).add_to(m)

# 4. Add a LayerControl so the user can toggle layers (useful if more layers are added)
folium.LayerControl().add_to(m)

# 5. Save the interactive map to an HTML file
m.save(OUTPUT_FILE)

print(f"\nInteractive map saved successfully to '{OUTPUT_FILE}'!")
print("Open this HTML file in your web browser to view the interactive map.")
