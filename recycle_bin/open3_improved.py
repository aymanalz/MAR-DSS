"""
Interactive Stream Finder Application

A Dash application that allows users to click on a map and find streams
within a specified radius of that location using OpenStreetMap data.
"""

import osmnx as ox
import geopandas as gpd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import transform
import pyproj
from typing import Tuple, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    """Application configuration settings."""
    PLACE_NAME = "Oakland, California, USA"
    STREAM_TAGS = {"waterway": ["stream", "river", "canal"]}
    RADIUS_MILES = 5
    RADIUS_METERS = RADIUS_MILES * 1609.34  # Convert miles to meters
    MAP_STYLE = "carto-positron"
    INITIAL_ZOOM = 10
    DETAIL_ZOOM = 11

class GeometryUtils:
    """Utility functions for geometric operations."""
    
    @staticmethod
    def create_circle_around_point(lat: float, lon: float, radius_meters: float) -> Polygon:
        """
        Create a circle around a point with the specified radius in meters.
        
        Args:
            lat: Latitude of the center point
            lon: Longitude of the center point
            radius_meters: Radius in meters
            
        Returns:
            Shapely Polygon representing the circle in WGS84
        """
        point = Point(lon, lat)
        
        # Define coordinate reference systems
        wgs84 = pyproj.CRS('EPSG:4326')
        web_mercator = pyproj.CRS('EPSG:3857')
        
        # Create transformers
        transformer = pyproj.Transformer.from_crs(wgs84, web_mercator, always_xy=True)
        transformer_back = pyproj.Transformer.from_crs(web_mercator, wgs84, always_xy=True)
        
        # Transform to Web Mercator, create buffer, transform back
        point_projected = transform(transformer.transform, point)
        circle_projected = point_projected.buffer(radius_meters)
        circle_wgs84 = transform(transformer_back.transform, circle_projected)
        
        return circle_wgs84
    
    @staticmethod
    def get_circle_bounds(circle: Polygon) -> Tuple[float, float, float, float]:
        """Get bounding box coordinates from a circle polygon."""
        return circle.bounds
    
    @staticmethod
    def create_bbox_polygon(bounds: Tuple[float, float, float, float]) -> Polygon:
        """Create a rectangular polygon from bounds."""
        minx, miny, maxx, maxy = bounds
        return Polygon([(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)])

class StreamFetcher:
    """Handles fetching streams from OpenStreetMap data."""
    
    def __init__(self, stream_tags: dict):
        self.stream_tags = stream_tags
    
    def fetch_streams_in_radius(self, lat: float, lon: float, radius_meters: float) -> gpd.GeoDataFrame:
        """
        Fetch streams within a specified radius of a point.
        
        Args:
            lat: Latitude of the center point
            lon: Longitude of the center point
            radius_meters: Search radius in meters
            
        Returns:
            GeoDataFrame containing stream geometries
        """
        try:
            logger.info(f"Searching for streams within {radius_meters:.0f}m of ({lat:.4f}, {lon:.4f})")
            
            # Create precise circular buffer
            circle = GeometryUtils.create_circle_around_point(lat, lon, radius_meters)
            
            # Get bounding box for OSM query
            bounds = GeometryUtils.get_circle_bounds(circle)
            bbox_polygon = GeometryUtils.create_bbox_polygon(bounds)
            
            logger.info(f"Bounding box: {bounds}")
            
            # Fetch features from OSM
            gdf_features = ox.features.features_from_polygon(
                bbox_polygon, tags=self.stream_tags
            )
            logger.info(f"Found {len(gdf_features)} total features")
            
            # Filter to linear geometries
            gdf_streams = gdf_features[
                gdf_features.geometry.geom_type.isin(['LineString', 'MultiLineString'])
            ].copy()
            logger.info(f"Found {len(gdf_streams)} linear stream features")
            
            # Filter streams that intersect with the precise circle
            gdf_streams = gdf_streams[gdf_streams.geometry.intersects(circle)]
            logger.info(f"After circle filtering: {len(gdf_streams)} streams")
            
            return gdf_streams
            
        except Exception as e:
            logger.error(f"Error fetching streams: {e}")
            return gpd.GeoDataFrame()

class CoordinateExtractor:
    """Handles extraction of coordinates from geometries for visualization."""
    
    @staticmethod
    def extract_line_coordinates(geometries) -> Tuple[List[float], List[float]]:
        """
        Extract coordinates from LineString or MultiLineString geometries.
        
        Args:
            geometries: GeoSeries of geometries
            
        Returns:
            Tuple of (latitudes, longitudes) lists with None separators
        """
        lats, lons = [], []
        
        def add_coords(geom):
            lons.extend([c[0] for c in geom.coords])
            lats.extend([c[1] for c in geom.coords])
            lons.append(None)
            lats.append(None)
        
        for geom in geometries:
            if geom.geom_type == 'LineString':
                add_coords(geom)
            elif geom.geom_type == 'MultiLineString':
                for line in geom.geoms:
                    add_coords(line)
        
        # Remove trailing None
        if lats and lats[-1] is None:
            lats.pop()
            lons.pop()
        
        return lats, lons

class MapVisualizer:
    """Handles map visualization and trace creation."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def create_base_figure(self, center_lat: float, center_lon: float) -> go.Figure:
        """Create the base map figure."""
        fig = go.Figure()
        fig.update_layout(
            title=f'Click anywhere to find streams within {self.config.RADIUS_MILES} miles',
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                style=self.config.MAP_STYLE,
                bearing=0,
                center=dict(lat=center_lat, lon=center_lon),
                pitch=0,
                zoom=self.config.INITIAL_ZOOM
            ),
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        return fig
    
    def create_stream_trace(self, lats: List[float], lons: List[float]) -> go.Scattermapbox:
        """Create a trace for stream visualization."""
        return go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='lines',
            line=dict(width=3, color='#1E90FF'),
            name='Streams and Rivers',
            hoverinfo='none'
        )
    
    def create_center_marker(self, lat: float, lon: float) -> go.Scattermapbox:
        """Create a marker for the clicked point."""
        return go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode='markers',
            marker=dict(size=12, color='red', symbol='circle'),
            name='Clicked Point',
            hoverinfo='text',
            hovertext=f'Center: ({lat:.4f}, {lon:.4f})'
        )
    
    def create_radius_circle(self, lat: float, lon: float, radius_meters: float) -> Optional[go.Scattermapbox]:
        """Create a trace for the radius circle."""
        try:
            circle = GeometryUtils.create_circle_around_point(lat, lon, radius_meters)
            if circle.geom_type == 'Polygon':
                circle_lons, circle_lats = circle.exterior.xy
                return go.Scattermapbox(
                    lat=list(circle_lats),
                    lon=list(circle_lons),
                    mode='lines',
                    line=dict(width=2, color='red', dash='dash'),
                    name=f'{self.config.RADIUS_MILES}-mile radius',
                    hoverinfo='none'
                )
        except Exception as e:
            logger.error(f"Error creating radius circle: {e}")
        return None

class StreamFinderApp:
    """Main application class."""
    
    def __init__(self):
        self.config = Config()
        self.stream_fetcher = StreamFetcher(self.config.STREAM_TAGS)
        self.coordinate_extractor = CoordinateExtractor()
        self.visualizer = MapVisualizer(self.config)
        self.center_lat = None
        self.center_lon = None
        self.app = None
        
    def initialize(self) -> bool:
        """Initialize the application and fetch initial data."""
        try:
            logger.info(f"Setting up initial map for {self.config.PLACE_NAME}")
            
            # Get boundary and center coordinates
            gdf_boundary = ox.geocode_to_gdf(self.config.PLACE_NAME)
            self.center_lat = gdf_boundary.geometry.centroid.y.iloc[0]
            self.center_lon = gdf_boundary.geometry.centroid.x.iloc[0]
            
            logger.info("Initial setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            return False
    
    def create_layout(self) -> html.Div:
        """Create the Dash layout."""
        return html.Div(
            style={'backgroundColor': '#f0f0f0', 'height': '100vh', 'padding': '20px'},
            children=[
                html.H1(
                    children=f'Interactive Stream Finder: {self.config.PLACE_NAME}',
                    style={
                        'textAlign': 'center',
                        'color': '#333333',
                        'fontFamily': 'Inter, sans-serif'
                    }
                ),
                html.Div(
                    children=f'Click anywhere on the map to find streams within {self.config.RADIUS_MILES} miles of that location.',
                    style={
                        'textAlign': 'center',
                        'color': '#555555',
                        'marginBottom': '20px',
                        'fontFamily': 'Inter, sans-serif'
                    }
                ),
                html.Div(
                    id='status-display',
                    children='Click on the map to start exploring streams!',
                    style={
                        'textAlign': 'center',
                        'color': '#666666',
                        'marginBottom': '10px',
                        'fontFamily': 'Inter, sans-serif',
                        'fontStyle': 'italic'
                    }
                ),
                dcc.Graph(
                    id='waterways-map',
                    figure=self.visualizer.create_base_figure(self.center_lat, self.center_lon),
                    style={'height': '80vh', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'borderRadius': '8px'}
                )
            ]
        )
    
    def setup_callbacks(self):
        """Setup Dash callbacks."""
        
        @self.app.callback(
            [Output('waterways-map', 'figure'),
             Output('status-display', 'children')],
            [Input('waterways-map', 'clickData')]
        )
        def update_map_on_click(clickData):
            """Handle map clicks and update visualization."""
            # Create base figure
            fig = go.Figure()
            fig.update_layout(
                mapbox=dict(
                    style=self.config.MAP_STYLE, 
                    zoom=self.config.INITIAL_ZOOM, 
                    center=dict(lat=self.center_lat, lon=self.center_lon)
                ),
                margin={"r": 0, "t": 40, "l": 0, "b": 0},
                autosize=True,
                hovermode='closest'
            )
            
            if clickData is None:
                status_text = 'Click on the map to start exploring streams!'
                fig.update_layout(title=f'Click anywhere to find streams within {self.config.RADIUS_MILES} miles')
                return fig, status_text
            
            # Extract click coordinates
            lat = clickData['points'][0]['lat']
            lon = clickData['points'][0]['lon']
            
            # Fetch streams
            gdf_streams = self.stream_fetcher.fetch_streams_in_radius(lat, lon, self.config.RADIUS_METERS)
            
            # Create traces
            traces = []
            
            if not gdf_streams.empty:
                # Add stream traces
                all_lats, all_lons = self.coordinate_extractor.extract_line_coordinates(gdf_streams.geometry)
                traces.append(self.visualizer.create_stream_trace(all_lats, all_lons))
                status_text = f'Found {len(gdf_streams)} streams within {self.config.RADIUS_MILES} miles of ({lat:.4f}, {lon:.4f})'
            else:
                status_text = f'No streams found within {self.config.RADIUS_MILES} miles of ({lat:.4f}, {lon:.4f})'
            
            # Add center marker and radius circle
            traces.append(self.visualizer.create_center_marker(lat, lon))
            
            radius_circle = self.visualizer.create_radius_circle(lat, lon, self.config.RADIUS_METERS)
            if radius_circle:
                traces.append(radius_circle)
            
            # Add all traces and update layout
            fig.add_traces(traces)
            fig.update_layout(
                title=f'Streams within {self.config.RADIUS_MILES} miles of ({lat:.4f}, {lon:.4f})',
                mapbox=dict(center=dict(lat=lat, lon=lon), zoom=self.config.DETAIL_ZOOM)
            )
            
            return fig, status_text
    
    def run(self):
        """Run the application."""
        if not self.initialize():
            logger.error("Failed to initialize application")
            return
        
        # Create Dash app
        self.app = Dash(__name__)
        self.app.layout = self.create_layout()
        self.setup_callbacks()
        
        logger.info("Starting application...")
        self.app.run(debug=True)

def main():
    """Main entry point."""
    app = StreamFinderApp()
    app.run()

if __name__ == '__main__':
    main()
