import os
import numpy as np
import rasterio
import rasterio.mask
import geopandas as gpd
from pystac_client import Client
import rioxarray

def read_polygon_and_create_bbox(geojson_file):
    farm_polygon = gpd.read_file(geojson_file)
    polygon = farm_polygon['geometry'][0]
    coordinates = polygon.exterior.coords if polygon.geom_type == 'Polygon' else polygon.geoms[0].exterior.coords
    flattened_coords = list(coordinates)
    min_x = min(coord[0] for coord in flattened_coords)
    min_y = min(coord[1] for coord in flattened_coords)
    max_x = max(coord[0] for coord in flattened_coords)
    max_y = max(coord[1] for coord in flattened_coords)
    bbox = [min_x, min_y, max_x, max_y]
    return bbox, farm_polygon, farm_polygon.crs

def fetch_sentinel_image(api_url, collections, bbox, start_date, end_date):
    client = Client.open(api_url)
    datetime_range = f"{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    print(f"Searching images from {datetime_range} within bbox {bbox}")
    search = client.search(collections=collections, bbox=bbox, datetime=datetime_range, max_items=10)
    items = search.item_collection()
    if len(items) == 0:
        raise ValueError("Imagery unavailable for the given location and date range.")
    return items[0]

def download_band(asset_href, output_path):
    band = rioxarray.open_rasterio(asset_href)
    band.rio.to_raster(output_path)
    return output_path

def clipper(sentinel_band_url, shapes, item):
    with rasterio.open(sentinel_band_url) as src:
        image_crs = src.crs
        if shapes.crs != image_crs:
            shapes = shapes.to_crs(image_crs)
        polygon = shapes['geometry'][0]
        out_image, out_transform = rasterio.mask.mask(src, [polygon], crop=True)
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})
    temp_file_path = f"temp_{item}.tif"
    with rasterio.open(temp_file_path, "w", **out_meta) as dest:
        dest.write(out_image)
    return temp_file_path

def write_tiff(file_path, data_array, meta_data):
    with rasterio.open(file_path, "w", **meta_data) as dest:
        dest.write(data_array, 1)
