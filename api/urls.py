from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    FailedPlanListView,
    PlanDetailView,
    PlanListCreateView,
    UploadPdfView,
    index,
    pulllist_can1,
    pulllist_hydro,
    pulllist_line3,
)
from django.views.generic import TemplateView
import os

urlpatterns = [
    path("", index),  # Root path
    path(
        "upload/", UploadPdfView.as_view(), name="upload"
    ),  # API endpoint for file uploads
    path(
        "plans/",
        PlanListCreateView.as_view(),
        name="plans_list_create",
    ),  # API for Plan
    path("plans/<int:pk>/", PlanDetailView.as_view(), name="plan_detail"),
    path("failed-plans/", FailedPlanListView.as_view(), name="failed_plans"),
    path("can1_pulllist/", pulllist_can1, name="pulllist_can1"),
    path("hydro_pulllist/", pulllist_hydro, name="pulllist_hydro"),
    path("line3_pulllist/", pulllist_line3, name="pulllist_line3"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=os.path.join(settings.BASE_DIR, "client/dist/client/browser/"),
    )
