import requests
import cv2
import numpy as np
import os
from moviepy.editor import ImageSequenceClip
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Define FastAPI app
app = FastAPI()

# Define request model
class ImageUrls(BaseModel):
    urls: List[str]

# Download an image from a URL
def download_image(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
    else:
        raise HTTPException(status_code=400, detail=f"Failed to download image from {url}")

# Endpoint to create a video from image URLs
@app.post("/create_video/")
async def create_video(image_urls: ImageUrls):
    img_folder = "temp_images"
    os.makedirs(img_folder, exist_ok=True)
    image_files = []

    try:
        # Download images and save locally
        for idx, url in enumerate(image_urls.urls):
            img_path = os.path.join(img_folder, f"image_{idx}.jpg")
            download_image(url, img_path)
            image_files.append(img_path)

        # Create video
        video_path = "output_video.mp4"
        clip = ImageSequenceClip(image_files, fps=1)
        clip.write_videofile(video_path)

        # Clean up images
        for img_file in image_files:
            os.remove(img_file)
        os.rmdir(img_folder)

        return {"video_path": video_path}
    except Exception as e:
        # Clean up on error
        for img_file in image_files:
            if os.path.exists(img_file):
                os.remove(img_file)
        os.rmdir(img_folder)
        raise HTTPException(status_code=500, detail=str(e))
