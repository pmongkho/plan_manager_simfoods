from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.generic import TemplateView


urlpatterns = [
    # Serve Angular index.html at the root
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]
