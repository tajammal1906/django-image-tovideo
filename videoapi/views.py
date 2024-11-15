import cv2
import requests
import numpy as np
import os
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view


@api_view(['POST'])
def create_video_from_images(request):
    # Get the array of image URLs from the POST request
    image_urls = request.data.get('image_urls', [])

    if not image_urls:
        return JsonResponse({'error': 'No image URLs provided'}, status=400)

    # Ensure the media directory exists
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
            images.append(image)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if not images:
        return JsonResponse({'error': 'Failed to load any valid images'}, status=400)

    # Set up video writer
    height, width, layers = images[0].shape
    # Use H.264 codec instead of mp4v for better compatibility
    fourcc = cv2.VideoWriter_fourcc(*'H264')

    video_filename = os.path.join(settings.MEDIA_ROOT, 'generated_video.mp4')

    # Write video to file
    video_writer = cv2.VideoWriter(video_filename, fourcc, 2, (width, height))  # 2 FPS
    for img in images:
        video_writer.write(img)
    video_writer.release()

    video_url = settings.MEDIA_URL + 'generated_video.mp4'
    return JsonResponse({'video_url': video_url})
