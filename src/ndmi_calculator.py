

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import read_polygon_and_create_bbox, fetch_sentinel_image, download_band, clipper, write_tiff
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def calculate_data(index_name, band_list, meta_details):
    fileName = meta_details['fileName']
    sensing_date = meta_details['sensingDate']
    shapes = meta_details['UTMshape']
    assets = meta_details['asset_data']
    temp_file_paths = []
    for item in band_list:
        sentinel_band_url = assets[item]['href']
        temp_file_path = clipper(sentinel_band_url, shapes, item)
        temp_file_paths.append(temp_file_path)
    with rasterio.open(temp_file_paths[0]) as src:
        bandA = src.read(1).astype(float)
        index_meta = src.meta.copy()
    with rasterio.open(temp_file_paths[1]) as src:
        bandB = src.read(1).astype(float)
    index_meta.update(dtype=rasterio.float32, count=1, compress='lzw')
    calc_index_array = np.divide(bandB - bandA, bandB + bandA, out=np.zeros_like(bandA, dtype=np.float32), where=(bandB + bandA) != 0)
    print(f"{index_name} Data created successfully")
    file_path = f"{fileName}_{sensing_date.strftime('%Y-%m-%d')}_{index_name}.tif"
    write_tiff(file_path, calc_index_array, index_meta)

        # Save as PNG
    png_file_path = f"{fileName}_{sensing_date.strftime('%Y-%m-%d')}_{index_name}.png"
    plt.imshow(calc_index_array, cmap='RdYlGn')  
    plt.colorbar()
    plt.title(f"{index_name} {sensing_date.strftime('%Y-%m-%d')}")
    plt.savefig(png_file_path)
    plt.close()

    for temp_file_path in temp_file_paths:
        os.remove(temp_file_path)
    return "Success"

def main(geojson_path, date, output_path):
    bbox, farm_polygon, _ = read_polygon_and_create_bbox(geojson_path)
    start_date = datetime.strptime(date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=5)
    try:
        item = fetch_sentinel_image(api_url="https://earth-search.aws.element84.com/v1", collections=["sentinel-2-l2a"], bbox=bbox, start_date=start_date, end_date=end_date)
        assets = item.assets
        print(f"Assets available: {list(assets.keys())}")
        nir_href = assets["nir08"].href
        swir_href = assets["swir16"].href
        sensing_date = item.datetime


        meta_details = {
            "fileName": output_path,
            "sensingDate": sensing_date,
            "UTMshape": farm_polygon,
            "asset_data": {
                "nir08": {"href": nir_href},
                "swir16": {"href": swir_href}
            }
        }
        band_list = ["nir08", "swir16"]
        calculate_data("NDMI", band_list, meta_details)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Calculate NDMI from Sentinel-2 Imagery.")
    parser.add_argument("geojson", type=str, help="GeoJSON file path for the farm polygon.")
    parser.add_argument("date", type=str, help="Date for the imagery in YYYY-MM-DD format.")
    parser.add_argument("output", type=str, help="Output path for the TIFF image.")
    args = parser.parse_args()
    main(args.geojson, args.date, args.output)
