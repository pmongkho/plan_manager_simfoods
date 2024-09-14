from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_and_process_files, name='upload_and_process_files'),
]
