from django.urls import path
import os
from django.conf import settings
from django.conf.urls.static import static
from api.views import (
    index,
    UploadPdfView,
    PlanListCreateView,
    PlanDetailView,
    FailedPlanListView,
    plans_can1,
    plans_hydro,
    plans_line3,
    update_plan_order,
    upload_weights_pdf,
    AdminManageDBView,
    ClearDatabaseView,
)

urlpatterns = [
    path("", index),  # Root path
    path("admin/upload-db/", AdminManageDBView.as_view(), name="admin-upload-pdf"),
    path(
        "admin/clear-database/",
        ClearDatabaseView.as_view(),
        name="admin-clear-database",
    ),
    path("upload/", UploadPdfView.as_view(), name="upload"),  # File uploads
    path("plans/", PlanListCreateView.as_view(), name="plans_list_create"),  # Plan API
    path("plans/<int:pk>/", PlanDetailView.as_view(), name="plan_detail"),
    path("plans/update-order/", update_plan_order, name="update-plan-order"),
    path("failed-plans/", FailedPlanListView.as_view(), name="failed_plans"),
    path("plans/can1/", plans_can1, name="plans_can1"),
    path("plans/hydro/", plans_hydro, name="plans_hydro"),
    path("plans/line3/", plans_line3, name="plans_line3"),
    path("upload_weights_pdf/", upload_weights_pdf, name="upload_weights_pdf"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=os.path.join(settings.BASE_DIR, "client/dist/client/browser/"),
    )
