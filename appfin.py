# app.py
from flask import Flask, render_template, request
import os

app = Flask(__name__)

# dictionaries.py
dict1 = {1: ['IfcMeasure', 'IfcPerson', 'IfcGeometricR.SubContext', 'IfcProject', 'IfcOwnerHistory', 
             'IfcPersonAndOrganization', 'IfcSIUnit', 'IfcConversionBasedUnit', 'IfcPostalAddress', 
             'IfcGeometricR.Context', 'IfcLocal', 'IfcSite', 'IfcApplication', 'IfcUnitAssignment', 
             'IfcAxis2Placement3D', 'IfcBuilding', 'IfcBuildingStorey', 'IfcOrganization', 
             'IfcDimensionalExponents', 'IfcCartesianPoint']}
combined_list = list(set(sum(dict1.values(), [])))

# Path to the IFC file
IFC_FILE_PATH = r'C:\Users\SRUJANA GOLLA\Desktop\IISc\prajwal\3D-BIM-main\3D-BIM-main\episode-09\models\mad_scientist_212.ifc'

@app.route('/')
def index():
    return render_template('ind1.html', keywords_and_indices=dict1)

@app.route('/search', methods=['POST'])
def search():
    selected_keywords = [keyword.lower() for keyword in request.form.getlist('keywords')]
    finlist = selected_keywords[0].split(',')
    print(finlist)
    
    found_lines = []

    # Search the IFC file for selected keywords
    with open(IFC_FILE_PATH, 'r') as f:
        for line in f:
            if any(keyword in line.lower() for keyword in finlist):
                found_lines.append(line.strip())

    return render_template('res.html', lines=found_lines, keywords=finlist)

if __name__ == '__main__':
    app.run(debug=True)
