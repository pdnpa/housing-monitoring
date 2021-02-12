# housing-monitoring

Python script to parse CSV file data (via json) into a sqlite database. Automatically generates the table schemas based on pre set filenames, headers, and data types.

## Data

completions.csv parsed into json data as follows

```
"Application_Number": "16251227 2184",
"Parish": "Alstonefield",
"Description": "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Curabitur",
"Address": "Ap #949-9453 Non, Street",
"Occupancy_Type": "Agricultural or Holiday",
"Application_Type": "VAR",
"FY": "2007/08",
"ISSUEDATE": "21/01/2008",
"District": "SMDC",
"Dwellings": "1"
```

## sqlite schema

![schema](https://github.com/pdnpa/housing-monitoring/blob/main/schema.png)

## sql JOIN table produced for analysis

**Num**|**Application_Number**|**FY**|**Quantity**|**Occupancy_Type**|**Build_Type**
:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
0|16030428|1991/92|1|Ancillary|COU
1|16440708|1991/92|1|Ancillary|COU
2|16180117|1991/92|1|Ancillary|COU
3|16180116|1991/92|1|Ancillary|NEW
4|16730127|1991/92|1|Holiday|COU
