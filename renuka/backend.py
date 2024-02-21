from flask import Flask, request, redirect, url_for, render_template
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client.user_activities_db  # Ensure this matches your database name

@app.route('/')
def index():
    return render_template('start.html')

@app.route('/survey')
def survey():
    return render_template('pleasefinalplease.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Convert form data to dict with lists as values
    data = request.form.to_dict(flat=False)
    processed_data = {}

    # Handle user information and single-value fields
    user_info_fields = ['name', 'age', 'gender', 'occupation', 'occupationType', 'maritalStatus']
    for field in user_info_fields:
        processed_data[field] = data.get(field, [None])[0]

    # Handle work/school timings
    processed_data['workSchoolTimings'] = {
        "from": data.get('timeFrom', [None])[0],
        "to": data.get('timeTo', [None])[0]
    }

    # Handle spaciousAreas checkboxes
    processed_data['spaciousAreas'] = data.get('spaciousArea[]', [])

    # Process 'mosttime[]' as a list of inputs
    processed_data['mosttime'] = data.get('mosttime[]', [])

    # Handle paragraph input 'userparagraph'
    processed_data['userparagraph'] = data.get('userparagraph', [None])[0]
    print("Paragraph data:", processed_data['userparagraph'])

    # Process time input form for multiple activities
    for key, value in data.items():
        if key.endswith('-toggle'):
            continue  # Skip processing toggles directly
        
        # Check if the toggle for "did not perform" is set for an activity
        activity_key = key.replace('[]', '')  # Normalize key name
        if f'{activity_key}-toggle' in data:
            processed_data[activity_key] = 'n/a'
        else:
            if key.endswith('[]') and key != 'mosttime[]':
                # Assuming each activity has pairs of time inputs
                times = [{'from': from_time, 'to': to_time} for from_time, to_time in zip(value[::2], value[1::2])]
                processed_data[activity_key] = times

    # Store processed data in MongoDB
    db.user_activities.insert_one(processed_data)
    
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    app.run(debug=True)
