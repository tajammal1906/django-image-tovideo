import cv2
import requests
import numpy as np
import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Ensure the media directory exists
MEDIA_DIR = "media"
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)


@app.route('/create_video_from_images', methods=['POST'])
def create_video_from_images():
    # Get the array of image URLs from the POST request
    data = request.get_json()
    image_urls = data.get('image_urls', [])

    if not image_urls:
        return jsonify({'error': 'No image URLs provided'}), 400

    images = []
    for url in image_urls:
        try:
            response = requests.get(url)
            image_data = np.asarray(bytearray(response.content), dtype=np.uint8)
            image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            if image is None:
                raise Exception(f"Could not decode image from {url}")
            images.append(image)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    if not images:
        return jsonify({'error': 'Failed to load any valid images'}), 400

    # Set up video writer
    height, width, layers = images[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    video_filename = os.path.join(MEDIA_DIR, 'generated_video.mp4')

    # Write video to file
    video_writer = cv2.VideoWriter(video_filename, fourcc, 2, (width, height))  # 2 FPS
    for img in images:
        video_writer.write(img)
    video_writer.release()

    return jsonify({'video_url': f"/media/generated_video.mp4"})


@app.route('/media/<filename>', methods=['GET'])
def serve_media(filename):
    return send_from_directory(MEDIA_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True)
