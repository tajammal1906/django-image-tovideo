import requests
import os
import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from tempfile import TemporaryDirectory

app = FastAPI()

class ImageUrls(BaseModel):
    urls: List[str]

def download_image(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
    else:
        raise HTTPException(status_code=400, detail=f"Failed to download image from {url}")

@app.post("/create_video/")
async def create_video(image_urls: ImageUrls):
    with TemporaryDirectory() as tmp_dir:
        image_files = []
        video_path = os.path.join(tmp_dir, "output_video.mp4")

        try:
            for idx, url in enumerate(image_urls.urls):
                img_path = os.path.join(tmp_dir, f"image_{idx}.jpg")
                download_image(url, img_path)
                image_files.append(img_path)

            # Create video using OpenCV
            frame = cv2.imread(image_files[0])
            height, width, _ = frame.shape
            out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 1, (width, height))

            for img_file in image_files:
                frame = cv2.imread(img_file)
                out.write(frame)
            out.release()

            # Return the video path for further handling (e.g., upload to S3)
            return {"video_path": video_path}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
