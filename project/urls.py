from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    # Serve Angular index.html at the root

    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    
]
