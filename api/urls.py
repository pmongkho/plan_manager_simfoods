from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import FailedPlanListView, PlanDetailView, PlanListCreateView, UploadPdfView, index
from django.views.generic import TemplateView

urlpatterns = [
    path("", index, name="index"),
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html")),
    path(
        "api/upload/", UploadPdfView.as_view(), name="upload"
    ),  # API endpoint for file uploads
    path(
        "api/plans/",
        PlanListCreateView.as_view(),
        name="plans_list_create",
    ),  # API for Plan
    path("api/plans/<int:pk>/", PlanDetailView.as_view(), name="plan_detail"),
    path("api/failed-plans/", FailedPlanListView.as_view(), name="failed_plans"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
