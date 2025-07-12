# Significant Disproportionality (SD) Geospatial Dashboard

A Python script for processing state education agency (SEA) significant disproportionality (SD) data and creating geospatial visualizations in ArcGIS Pro.

## Overview

This script processes SD data to create interactive geospatial layers showing SD indicators across school districts. It handles both traditional districts (with boundary shapefiles) and charter schools (with lat/long coordinates) to provide comprehensive statewide coverage.

## Features

- **Data Processing**: Cleans and standardizes SEA SD data with demographic information
- **Geospatial Mapping**: Creates ArcGIS layers for traditional districts and charter schools
- **Multiple Indicators**: Supports discipline, representation, and placement SD categories
- **Multi-Year Analysis**: Processes cluster reported data across multiple school years
- **Demographic Breakdown**: Analyzes SD patterns by race/ethnicity

## Requirements

### Software

- ArcGIS Pro (compatible with ArcGIS Pro 3.x)
- Python environment with the packages:
  - `arcpy` (ArcGIS Python library)
  - `pandas`
  - `numpy`
  - `itertools`

### Data Files Required

The script expects the following file structure:

```
\\your-file-path\Significant_Disproportionality\Dashboard\
├── RawData\
│   ├── Education_Data.csv        # Main education SD data
│   └── DistLatLong.csv          # Charter district coordinates
├── DistrictShapefile\
│   └── Current_Districts.shp     # Traditional district boundaries
└── CleanData\                    # Output directory (local)
```
> [!WARNING]
> User humans must ensure that no student-level information is included in the data. When aggregating student-level data to the district level, users must apply masking to any count less than five to protect student privacy and comply with the Family Educational Rights and Privacy Act (FERPA).

## Data Dictionaries

### Race/Ethnicity Codes

- `WHI`: White
- `HISP`: Hispanic
- `BLA`: Black or African American
- `ASI`: Asian
- `TMR`: Two or More Races
- `AIAN`: American Indian and Alaska Native
- `PAI`: Pacific Islander

### SD Indicator Categories

**Discipline Indicators:**

- `ISSMT10`: In School Suspension > 10 days
- `TDR`: Total Disciplinary Removal
- `OSSELTE10`: Out of School Suspension or Expulsion ≤ 10 days
- `OSSEMT10`: Out of School Suspension or Expulsion > 10 days
- `ISSLTE10`: In School Suspension ≤ 10 days

**Representation Indicators:**

- `ID`: Intellectual Disability
- `ED`: Emotional Disturbance
- `REP`: All Disabilities
- `AUT`: Autism
- `OHI`: Other Health Impairment
- `SLI`: Speech/Language Impairment
- `SLD`: Specific Learning Disability

**Placement Indicators:**

- `SS`: Separate Schools and Residential Facilities
- `RCLT40`: Regular Class Placement < 40%

## Usage

1. **Setup**: Ensure ArcGIS Pro is open with an active map
1. **Configure Paths**: Update file paths in the script if needed
1. **Run Script**: Execute in ArcGIS Pro Python environment

```python
# The script will automatically:
# 1. Load and clean SEA data
# 2. Process demographics and SD indicators
# 3. Create geospatial layers
# 4. Apply symbology
```

## Outputs

### CSV Files (CleanData directory)

- `Table_ChartData.csv`: Complete dataset for dashboard charts
- `Table_CharterDistricts.csv`: Charter school data with coordinates
- `Table_{YEAR}_{INDICATOR}_{RACE}.csv`: Individual data slices

### ArcGIS Layers

- `Layer_All_SDs_merge`: All traditional districts with SD designations
- `Layer_All_Charters`: Charter schools with SD designations
- `Current_Districts`: District boundary outlines

## Important Notes

### Data Validation

- **Missing Coordinates**: Script includes manual fixes for districts missing lat/long data
- **Charter Districts**: Two districts (101813, 57837) have hardcoded coordinates
- **Annual Updates**: Coordinate fixes may need updating each year

### Manual Verification Required

The script will pause and display any districts missing coordinates:

```python
print(df_charter.loc[df_charter.Lat.isna()==True])
```

**Always review this output** and update coordinate fixes as needed.

### File Dependencies

- Script requires specific CSV column structure from SEA data exports
- Shapefile must contain `DISTRICT_N` field matching district codes
- Lat/long file format: skip 6 rows, columns 2-4 contain ID, Lat, Long

## Symbology

- **SD Districts**: Blue fill (RGB: 0, 112, 255) with transparency
- **Charter Schools**: Blue points, size 8
- **District Boundaries**: Black outline, no fill

## Troubleshooting

### Common Issues

1. **File Path Errors**: Verify network drive accessibility
1. **Missing Shapefiles**: Ensure district boundaries are current
1. **Coordinate Issues**: Check console output for missing lat/long data
1. **ArcGIS Licensing**: Verify ArcGIS Pro Advanced license for full functionality

### Performance Notes

- Processing time varies with dataset size (typically 5-15 minutes)
- Large datasets may require increased system memory
- Network drive access can affect performance

-----

*Last Updated: July 12, 2025*
