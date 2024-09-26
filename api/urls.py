from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_view, name="upload"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
]
