from flask import Flask, render_template
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="prajwal"
        )
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")
        return None

def execute_read_query(connection, query, params=None):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Error as e:
        print(f"The error '{e}' occurred")
        return []

def get_data():
    connection = create_connection()
    if connection:
        scorevalue = {'Biweekly': 1, 'Weekly': 2, 'Daily': 3, 'Monthly': 4, 'Bimonthly': 5, 'Very easy': 1, 'easy': 2, 'neither easy nor difficult': 3, 'difficult': 4, 'very difficult': 5, 'Excellently defined': 1, 'Reasonably defined': 2, 'Neutral': 3, 'Not so well defined': 4, 'Poorly defined': 5, 'Not important': 1, 'Some error is fine': 2, 'Important': 4, 'very Important': 5, 'very rarely': 1, 'rarely': 2, 'occasionally': 3, 'regularly': 4, 'very regularly': 5, 'yes': 1, 'likely': 2, 'Not sure': 3, 'Unlikely': 4, 'No': 5, 'Excellent': 1, 'Good': 2, 'Adequate': 3, 'Poor': 4, 'Very poor': 5, 'Highly centralized': 1, 'Moderately centralized': 2, 'Decentralized': 3, 'Moderately fragmented': 4, 'Highly fragmented': 5}

        # Get names
        distinct_names_query = "SELECT DISTINCT fname FROM responses"
        distinct_names = execute_read_query(connection, distinct_names_query)
        names = [name[0] for name in distinct_names]

        # Get people
        distinct_people_query = "SELECT DISTINCT human FROM responses"
        distinct_people = execute_read_query(connection, distinct_people_query)
        people = [person[0] for person in distinct_people]

        # Combine and deduplicate names and people
        all_names = list(set(names + people))

        # Get distinct questions, pair them, and prepare tabs data
        question_query = "SELECT DISTINCT question FROM responses ORDER BY question"
        questions = execute_read_query(connection, question_query)
        
        # Handle the case where there's an odd number of questions by adding the last one as a single-question tab
        if len(questions) % 2 != 0:
            questions.append(('Single',))  # Add a placeholder

        question_pairs = [questions[i:i+2] for i in range(0, len(questions), 2)]

        tabs_data = []  # Data for all tabs
        for pair in question_pairs:
            if len(pair) == 1:  # Single question handling
                tab_name = pair[0][0]
            else:
                tab_name = ''.join([q[0] for q in pair])  # Tab name as 'AB', 'CD', etc.
            
            data = []
            for name in names:
                row = [name]  # Add name label to the row
                green=0
                red=0
                for person in people:
                    responses = []
                    cell_bg = "white"  # Default background color
                    for question in pair:

                        query = "SELECT response FROM responses WHERE fname=%s AND human=%s AND question=%s"
                        params = (name, person, question[0])
                        values = execute_read_query(connection, query, params)
                        response = values[0][0] if values else "No Response"
                        responses.append(response)
                    
                    # Calculate scores with a default score of 5 if not found in the dictionary
                    scores = [scorevalue.get(resp, 5) for resp in responses]
                    if "No Response" not in responses:
                        if scores[0] >= scores[1]:
                            cell_bg = "#B6FF7D"
                            green+=1
                        elif scores[1] > scores[0]:
                            cell_bg = "#FF7474"
                            red+=1
                    
                    # Format cell content
                    
                    cell_content = f"{pair[0][0]}: {responses[0]}<br>{pair[1][0]}: {responses[1]}" if len(pair) == 2 else f"{pair[0][0]}: {responses[0]}"
                    row.append((cell_content, cell_bg))
                data.append(row)

                total_color_cells = green + red
                if total_color_cells > 0:
                    percentage = (green / total_color_cells) * 100
                else:
                    percentage=0
                
                row.append(percentage)
                data.append(row)
            
            tabs_data.append((tab_name, data))

        # Calculate green percentages for rows and columns
        row_col_data = []
        for name in all_names:
            row_data = {"name": name, "row_green": 0, "row_total": 0, "col_green": 0, "col_total": 0}
            # Row green calculation
            if name in names:
                for person in people:
                    green_count = sum(1 for tab_name, data in tabs_data for row in data if row[0] == name and any(cell[1] == "#B6FF7D" for cell in row[1:-1]))
                    total_count = sum(1 for tab_name, data in tabs_data for row in data if row[0] == name)
                    row_data["row_green"] = green_count
                    row_data["row_total"] = total_count
            
            # Column green calculation
            if name in people:
                for tab_name, data in tabs_data:
                    for row in data:
                        for idx, cell in enumerate(row[1:-1]):
                            if idx < len(people) and people[idx] == name:
                                if cell[1] == "#B6FF7D":
                                    row_data["col_green"] += 1
                                row_data["col_total"] += 1
            
            row_col_data.append(row_data)

        connection.close()
        return names, people, tabs_data, row_col_data
    else:
        return [], [], [], []

@app.route('/')
def home():
    names, people, tabs_data, row_col_data = get_data()
    return render_template('final15.html', names=names, people=people, tabs_data=tabs_data, row_col_data=row_col_data)


if __name__ == '__main__':
    app.run(debug=True)
