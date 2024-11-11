import cv2
import requests
import numpy as np
import os
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from io import BytesIO

@api_view(['POST'])
def create_video_from_images(request):
    image_urls = request.data.get('image_urls', [])
    if not image_urls:
        return JsonResponse({'error': 'No image URLs provided'}, status=400)

    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)

    images = []
    for url in image_urls:
        try:
            response = requests.get(url)
            image_data = np.asarray(bytearray(response.content), dtype=np.uint8)
            image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            if image is None:
                raise Exception(f"Could not decode image from {url}")
            
            # Resize image to reduce resolution
            scaled_image = cv2.resize(image, (640, 480))  # Adjust resolution
            images.append(scaled_image)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if not images:
        return JsonResponse({'error': 'Failed to load any valid images'}, status=400)

    height, width, layers = images[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_filename = os.path.join(settings.MEDIA_ROOT, 'generated_video.mp4')

    video_writer = cv2.VideoWriter(video_filename, fourcc, 2, (width, height))
    for img in images:
        video_writer.write(img)
    video_writer.release()

    video_url = settings.MEDIA_URL + 'generated_video.mp4'
    return JsonResponse({'video_url': video_url})
