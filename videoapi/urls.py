from django.urls import path
from .views import create_video_from_images

urlpatterns = [
    path('create_video/', create_video_from_images, name='create_video_from_images'),
]
