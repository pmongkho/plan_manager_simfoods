from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from api.views import (
    index,
    UploadPdfView,
    PlanListCreateView,
    PlanDetailView,
    FailedPlanListView,
    pulllist_can1,
    pulllist_hydro,
    pulllist_line3,
    plans_can1,
    plans_hydro,
    plans_line3
    ,
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
    path("pulllist/can1/", pulllist_can1, name="pulllist_can1"),
    path("pulllist/hydro/", pulllist_hydro, name="pulllist_hydro"),
    path("pulllist/line3/", pulllist_line3, name="pulllist_line3"),
    path("plans/can1/", plans_can1, name="plans_can1"),
    path("plans/hydro/", plans_hydro, name="plans_hydro"),
    path("plans/line3/", plans_line3, name="plans_line3"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=os.path.join(settings.BASE_DIR, "client/dist/client/browser/"),
    )
