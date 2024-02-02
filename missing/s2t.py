from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('frontend_images.html')  # Make sure the HTML file is named 'index.html' and is placed in the 'templates' directory

@app.route('/submit-data', methods=['POST'])
def handle_data():
    print("Files received:", request.files)  # printing the files received in the request
    text_input = request.form['textInput']
    # text splitting breakpoint
    parts = text_input.split("$#%&*")  # This is just an example; adjust according to your actual split logic

    # Create folders based on parts
    for i, part in enumerate(parts, start=1):
        folder_path = os.path.join('uploadss', f'Part{i}') #name of the folder that gets created
        os.makedirs(folder_path, exist_ok=True)

        # Save files for each part
        if f'imagesPart{i}' in request.files:
            file = request.files[f'imagesPart{i}']
            if file.filename:
                filename = file.filename
                file_path = os.path.join(folder_path, filename)
                file.save(file_path)

    return jsonify({"message": "Data and images processed successfully"}), 200

if __name__ == '__main__':
    # Ensure the 'uploadss' directory exists
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
