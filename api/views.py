# api/views.py

import os
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
    ListAPIView,
)
from rest_framework.response import Response
from rest_framework import status
from django.core.files import File
from api.files.pdf_plan_manager import PdfPlanSorter
from .models import FailedPlan, Page, Plan, SortedPDF, Weight
from .serializers import FailedPlanSerializer, PdfUploadSerializer, PlanSerializer
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view


# Test function to check if the user is an admin
def is_admin_user(user):
    return user.is_superuser

class PlanListCreateView(ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

class PlanDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    lookup_field = "pk"  # We will use the primary key to identify the plan

@method_decorator(user_passes_test(lambda u: u.is_staff), name="dispatch")
class UploadPdfView(CreateAPIView):
    serializer_class = PdfUploadSerializer

    def perform_create(self, serializer):
        """Override this method to save the uploaded files to the model if needed."""
        # If you want to store the files in the database using a model, you can use serializer.save()
        serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the uploaded files (to model, if needed)
            self.perform_create(serializer)

            # Process the uploaded data (file handling and processing logic)
            self.perform_upload_processing(serializer.validated_data)

            return Response(
                {"message": "Upload and processing successful"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FailedPlanListView(ListAPIView):
    queryset = FailedPlan.objects.all()
    serializer_class = FailedPlanSerializer


def index(request):
    return render(request, 'index.html')

# Common function to handle the aggregation
def get_plan_pulllist_by_line(start_plan_id, end_plan_id, line_type):
    plans = Plan.objects.filter(
        plan_id__gte=start_plan_id, plan_id__lte=end_plan_id, line=line_type
    )
    pulllist = (
        Weight.objects.filter(plan__in=plans)
        .values("component")
        .annotate(total_quantity=Sum("quantity"))
    )
    return pulllist


# View for "can1" line
@api_view(["GET"])
def pulllist_can1(request):
    start_plan_id = request.GET.get("start_plan_id")
    end_plan_id = request.GET.get("end_plan_id")

    if not start_plan_id or not end_plan_id:
        return JsonResponse(
            {"error": "Please provide both start and end plan IDs"}, status=400
        )

    try:
        pulllist = get_plan_pulllist_by_line(start_plan_id, end_plan_id, "can1")
        return JsonResponse(list(pulllist), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# View for "hydro" line
@api_view(["GET"])
def pulllist_hydro(request):
    start_plan_id = request.GET.get("start_plan_id")
    end_plan_id = request.GET.get("end_plan_id")

    if not start_plan_id or not end_plan_id:
        return JsonResponse(
            {"error": "Please provide both start and end plan IDs"}, status=400
        )

    try:
        pulllist = get_plan_pulllist_by_line(start_plan_id, end_plan_id, "hydro")
        return JsonResponse(list(pulllist), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# View for "line3"
@api_view(["GET"])
def pulllist_line3(request):
    start_plan_id = request.GET.get("start_plan_id")
    end_plan_id = request.GET.get("end_plan_id")

    if not start_plan_id or not end_plan_id:
        return JsonResponse(
            {"error": "Please provide both start and end plan IDs"}, status=400
        )

    try:
        pulllist = get_plan_pulllist_by_line(start_plan_id, end_plan_id, "line3")
        return JsonResponse(list(pulllist), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
