# Calculating Sentinel-2 NDMI with NIR08 and SWIR16
calculates the Normalized Difference Moisture Index (NDMI) from Sentinel-2 
imagery using a specified farm polygon in GeoJSON format.
This code  doesnt filter out cloudy images.

## Structure
sentinel_ndmi/
├── data/
│ └── farm_extent.geojson
├── outputs/
│ └── ndmi_output.tif
├── src/
│ ├── init.py
│ ├── ndmi_calculator.py
│ └── utils.py
├── tests/
│ └── test_ndmi_calculator.py
├── .gitignore
├── README.md
└── requirements.txt
