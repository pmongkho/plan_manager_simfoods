from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("upload/", views.upload_view, name="upload"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
