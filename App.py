from flask import Flask, request, jsonify, send_from_directory
from roboflow import Roboflow
from werkzeug.utils import secure_filename
import os
import threading
import shutil
import time

rf = Roboflow(api_key="1vhzvWYm1kwDHeUQd1G6")
project = rf.workspace().project("smartassistivedevice")
model = project.version(1).model

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['OUTPUT_FOLDER']):
    os.makedirs(app.config['OUTPUT_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

data = []
output = []

@app.route('/data', methods=['POST'])
def post_data():
    if 'imageFile' not in request.files:
        return jsonify({'error': 'Missing data, imageFile is required'}), 400

    file = request.files['imageFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        var = {
            'imageFile': filepath
        }
        data.append(var)
        return jsonify({'message': 'Data inserted'}), 201
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/output', methods=['GET'])
def get_output():
    if output:
        return jsonify(output[-1]), 200
    else:
        return jsonify({'message': 'No output data available'}), 200

@app.route('/outputs/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

def process_output():
    while True:
        if data:
            latest_image_data = data.pop(0)
            filepath = latest_image_data['imageFile']

            prediction_result = model.predict(filepath, confidence=40, overlap=30).json()
            
            output_filename = "prediction.jpg"
            output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            if prediction_result['predictions']:
                model.predict(filepath, confidence=40, overlap=30).save(output_filepath)
                for prediction in prediction_result['predictions']:
                    var = {
                        'imageFile': filepath,
                        'class': prediction['class'],
                        'confidence': prediction['confidence'],
                        'x': prediction['x'],
                        'y': prediction['y'],
                        'width': prediction['width'],
                        'height': prediction['height'],
                        'imageOutput': output_filename
                    }
                    output.append(var)
                
                print(f"Processed: {var}")
            else:
                var = {
                    'imageFile': filepath,
                    'class': None,
                    'confidence': None,
                    'x': None,
                    'y': None,
                    'width': None,
                    'height': None,
                    'imageOutput': output_filename
                }
                output.append(var)
                
                shutil.copy(filepath, output_filepath)
                
                print("No predictions found for the image.")
                print(f"Saved: {var}")
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=process_output, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
