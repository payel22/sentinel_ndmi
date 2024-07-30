import pytest
from src.ndmi_calculator import calculate_data, main

def test_calculate_data():
    meta_details = {
        "fileName": "outputs/test",
        "sensingDate": "2024-04-10",
        "UTMshape": None,  
        "asset_data": {
            "nir08": {"href": "path/to/nir_band.tif"},
            "swir16": {"href": "path/to/swir_band.tif"}
        }
    }
    band_list = ["nir08", "swir16"]
    result = calculate_data("NDMI", band_list, meta_details)
    assert result == "Success"

def test_main():
    geojson_path = 'data/farm_extent.geojson'
    date = '2023-10-13'
    output_path = 'outputs/ndmi_'
    main(geojson_path, date, output_path)
    assert os.path.exists(f'{output_path}_2024-04-10_NDMI.tif')
