import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point, box


def nearest_stream_bbox(lat, lon, dist_meters=2000):
    """
    Finds the nearest point on an OpenStreetMap waterway line to a given lat/lon
    within a specified search radius.

    Args:
        lat (float): The latitude of the starting point.
        lon (float): The longitude of the starting point.
        dist_meters (int): Search radius in meters to query OSM.

    Returns:
        dict: A dictionary containing the snapped lat/lon point and the distance
              moved in meters, or an error message.
    """
    # 1. Define the input point in WGS 84 (EPSG:4326)
    # Shapely Point is (lon, lat)
    point_4326 = Point(lon, lat)

    # --- 2. Define Bounding Box ---
    # Approximate meters -> degrees (1 degree latitude is approx 111,000 meters)
    deg_buffer = dist_meters / 111_000
    north = lat + deg_buffer
    south = lat - deg_buffer
    east = lon + deg_buffer
    west = lon - deg_buffer
    bbox_poly = box(west, south, east, north)

    # --- 3. Query OSM for Waterways (waterway=*) ---
    tags = {"waterway": True}

    try:
        # Query OSM using the polygon, result is in EPSG:4326
        waterways = ox.geometries_from_polygon(bbox_poly, tags)
    except Exception as e:
        return {"error": f"OSM query failed: {e}"}

    if waterways.empty:
        return {"error": "No streams found in search area."}

    # --- 4. Filter, Reproject, and Explode ---

    # 4a. Filter to keep only LineString and MultiLineString geometries
    # 'set_crs' is used for robustness as ox.geometries_from_polygon
    # might not explicitly set the CRS attribute
    waterways = (
        waterways[waterways.geom_type.isin(["LineString", "MultiLineString"])]
        .copy()
        .set_crs("EPSG:4326", allow_override=True)
    )

    if waterways.empty:
        return {"error": "No LineString streams found in search area."}

    # 4b. Reproject both the waterways and the point to Web Mercator (EPSG:3857)
    # for accurate distance calculations in meters.
    waterways_3857 = waterways.to_crs(epsg=3857)
    pt_3857 = (
        gpd.GeoSeries([point_4326], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]
    )

    # 4c. Explode MultiLineStrings into individual LineStrings.
    # This is crucial for calculating the distance to *every* segment.
    water_lines_exploded = waterways_3857.explode(
        ignore_index=True, to_container=True
    )

    # --- 5. Find Nearest Stream Segment ---

    # Compute the distance from the point to every stream segment
    water_lines_exploded["dist"] = water_lines_exploded.distance(pt_3857)

    # Find the minimum distance and the corresponding geometry
    nearest_idx = water_lines_exploded["dist"].idxmin()
    nearest_stream_geom = water_lines_exploded.loc[nearest_idx].geometry
    nearest_dist = water_lines_exploded.loc[nearest_idx]["dist"]

    # --- 6. Snap Point to the Nearest Stream ---

    # Calculate the fraction along the line that is closest to the point
    projection_fraction = nearest_stream_geom.project(pt_3857)

    # Interpolate (find the point) at that fraction along the line
    nearest_point_on_stream_3857 = nearest_stream_geom.interpolate(
        projection_fraction
    )

    # --- 7. Convert Result Back to Lat/Lon ---

    # Convert the snapped Point back to EPSG:4326
    snapped_lonlat = (
        gpd.GeoSeries([nearest_point_on_stream_3857], crs="EPSG:3857")
        .to_crs(epsg=4326)
        .iloc[0]
    )

    # The result is returned as (lat, lon)
    return {
        "snapped_point": (snapped_lonlat.y, snapped_lonlat.x),
        "distance_m": float(nearest_dist),
    }


# ==============================================================================
# Example Usage
# ==============================================================================

# Example 1: A point near Sacramento (38.5816, -121.4944)
# This point is slightly off the Sacramento River.
print("--- Example 1: Point near Sacramento River ---")
result_sacramento = nearest_stream_bbox(38.5816, -121.4944)
print(result_sacramento)

# Example 2: A point far from any major stream (e.g., in the middle of a desert)
# This should trigger the 'No streams found' error or a large distance.
# Let's try a point in the Nevada desert.
print("\n--- Example 2: Point in Nevada Desert ---")
result_desert = nearest_stream_bbox(
    39.5, -118.0, dist_meters=100
)  # Small search radius
print(result_desert)
