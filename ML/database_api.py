import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define the upload folder
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit file size to 50MB

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/upload_blob', methods=['POST'])
def upload_blob():
    """
    Endpoint to handle blob file upload and save each frame with a unique filename.
    """
    app.logger.debug("Received POST request on /upload_blob")

    if 'video' not in request.files:
        app.logger.error("No video file in the request")
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    if not latitude or not longitude:
        app.logger.error("Missing latitude or longitude in the request")
        return jsonify({"error": "Missing latitude or longitude"}), 400

    # Generate a unique filename using timestamp
    timestamp = int(time.time() * 1000)  # Milliseconds since epoch
    filename = secure_filename(f"{timestamp}_{video_file.filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Save the video frame
    video_file.save(file_path)
    app.logger.info(f"Frame saved at {file_path} with metadata: latitude={latitude}, longitude={longitude}")

    # Save metadata (latitude and longitude) to a text file
    metadata_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_metadata.txt")
    with open(metadata_file, 'w') as f:
        f.write(f"Latitude: {latitude}\nLongitude: {longitude}\n")

    app.logger.info(f"Metadata saved at {metadata_file}")
    return jsonify({"message": "Frame and metadata saved successfully"}), 200


@app.after_request
def add_cors_headers(response):
    """
    Adds CORS headers to every response for frontend compatibility.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


if __name__ == '__main__':
    app.run(debug=True)
