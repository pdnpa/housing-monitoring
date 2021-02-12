################################
#### Housing Database pdnpa ####
################################

import sqlite3
import csv
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

#### Input the csv data and convert to json file ####

# Input the csv file paths & set json to r/
csvFilePath = input('Enter .csv file:')
if len(csvFilePath) < 1 : csvFilePath = r'completions.csv'

jsonFilePath = r'completions.json'

# Function to convert a CSV to JSON takes the file paths as arguments
def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []

    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)

        # Convert each row into a dictionary and add it to data
        for row in csvReader:
            #add this python dict to json array
            jsonArray.append(row)

    #convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)

# Call the make_json function
csv_to_json(csvFilePath, jsonFilePath)

#### input json to DBsqlite file #####

# Open database connection
conn = sqlite3.connect('housing-data.sqlite')
cur = conn.cursor()

# Create tables or delete their content
cur.executescript('''
DROP TABLE IF EXISTS Application;
DROP TABLE IF EXISTS Build;
DROP TABLE IF EXISTS Occupancy;
DROP TABLE IF EXISTS Dwelling_items;

CREATE TABLE Application (
            id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            Application_Number  TEXT UNIQUE,
            Address  TEXT,
            Description TEXT,
            Parish TEXT,
            Issue_Date TEXT);

CREATE TABLE Build (
            id  INTEGER NOT NULL PRIMARY KEY,
            Build_Type Text UNIQUE);

CREATE TABLE Occupancy (
            id  INTEGER NOT NULL PRIMARY KEY,
            Occupancy_Type TEXT UNIQUE);

CREATE TABLE Dwelling_items (
            Application_id  INTEGER,
            Occupancy_id  INTEGER,
            Build_id  INTEGER,
            Quantity  INTEGER,
            FY INTEGER
            )
''')

#### Parse the json into the tables ####
str_data = open(r'completions.json').read()
json_data = json.loads(str_data)

for entry in json_data:
    Application_Number = entry['Application_Number'];
    Parish = entry['Parish'];
    Description = entry['Description'];
    Address = entry['Address'];
    Occupancy_Type = entry['Occupancy_Type'];
    Application_Type = entry['Application_Type'];
    FY = entry['FY'];
    ISSUEDATE = entry['ISSUEDATE'];
    District = entry['District'];
    Dwellings = entry['Dwellings'];

    cur.execute('''INSERT OR IGNORE INTO Build (Build_Type)
        VALUES ( ? )''', ( Application_Type, ) )
    cur.execute('SELECT id FROM Build WHERE Build_Type = ? ', (Application_Type, ))
    Build_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Occupancy (Occupancy_Type)
        VALUES ( ? )''', ( Occupancy_Type, ) )
    cur.execute('SELECT id FROM Occupancy WHERE Occupancy_Type = ? ', (Occupancy_Type, ))
    Occupancy_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Application (Application_Number, Address, Description, Parish, Issue_Date)
        VALUES ( ?, ?, ?, ?, ? )''', ( Application_Number, Address, Description, Parish, ISSUEDATE, ) )
    cur.execute('SELECT id FROM Application WHERE Application_Number = ? ', (Application_Number, ))
    Application_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Dwelling_items
        (Application_id, Occupancy_id, Build_id, Quantity, FY) VALUES ( ?, ?, ?, ?, ? )''',
        ( Application_id, Occupancy_id, Build_id, Dwellings, FY ) )

conn.commit()

#### Create a JOIN query to retrieve data into a pandas dataframe for analysis ####
table = pd.read_sql('''SELECT Application.Application_Number, Dwelling_items.FY, Dwelling_items.Quantity, Occupancy.Occupancy_Type, Build.Build_Type
            FROM Application JOIN Dwelling_items JOIN Occupancy JOIN Build
            ON Dwelling_items.Application_id = Application.ID and Dwelling_items.Occupancy_id = Occupancy.id
            AND Dwelling_items.Build_id = Build.id
            ORDER BY Dwelling_items.FY''', conn)

# print the data for checking
print(table)

# create a NET pivot table
net = pd.pivot_table(table, values = 'Quantity', index = 'Occupancy_Type', columns = 'FY', aggfunc = np.sum, margins = True )

# print the data for checking
print(net)

# create a GROSS pivot table by dropping - VALUES pandas.DataFrame.select_dtypes.html
table_gross = table[table.select_dtypes(include=[np.number]).ge(0).all(1)]
gross = pd.pivot_table(table_gross, values = 'Quantity', index = 'Occupancy_Type', columns = 'FY', aggfunc = np.sum, margins = True )

# print the data for checking
print(gross)

#### Output to csv as an example ####
with open("Output.csv", 'w') as _file:
    _file.write(net.to_csv() + "\n\n" + gross.to_csv())

print("Code has completed at " + str(datetime.now()))

cur.close()
