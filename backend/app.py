import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from pipeline.internet_plagiarism_detector import InternetPlagiarismDetector

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for React frontend

# Initialize detector
detector = InternetPlagiarismDetector(app.config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_DIR'], exist_ok=True)

@app.route('/api/check-internet-plagiarism', methods=['POST'])
def check_internet_plagiarism():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    try:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        results = detector.detect_internet_plagiarism(filepath)
        
        os.remove(filepath)
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)