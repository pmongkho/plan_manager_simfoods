# api/views.py

import os
from rest_framework.response import Response  # Use DRF's Response
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
from django.db.models import Sum, F
from rest_framework.permissions import IsAdminUser


class PlanListCreateView(ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdminUser]  # Only allow admin users


class PlanDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    lookup_field = "pk"  # We will use the primary key to identify the plan


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
    return render(request, "index.html")


@api_view(["GET"])
def pulllist_can1(request):
    return pulllist(request, "can1")


@api_view(["GET"])
def pulllist_hydro(request):
    return pulllist(request, "hydro")


@api_view(["GET"])
def pulllist_line3(request):
    return pulllist(request, "line3")


@api_view(["GET"])
def plans_can1(request):
    return plans(request, "can1")


@api_view(["GET"])
def plans_hydro(request):
    return plans(request, "hydro")


@api_view(["GET"])
def plans_line3(request):
    return plans(request, "line3")


def plans(request, line_type):
    try:
        # Filter plans by line_type (e.g., 'can1', 'hydro', 'line3')
        plans = Plan.objects.filter(line=line_type)

        # Prepare the response data by converting each plan to a dictionary
        response_data = []
        for plan in plans:
            pages = Page.objects.filter(plan=plan).values("front_page", "back_page")
            weights = Weight.objects.filter(plan=plan).values("component", "quantity")

            plan_data = {
                "plan_id": plan.plan_id,
                "batches": plan.batches,
                "progress": plan.progress,
                "order": plan.order,
                "line": plan.line,
                "pages": list(pages),
                "weights": list(weights),
            }
            response_data.append(plan_data)

        # Use DRF's Response to return the response
        return Response(response_data)

    except Exception as e:
        # Handle any exceptions and return an error response
        return Response({"error": str(e)}, status=500)


def pulllist(request, line_type):
    start_plan_id = request.query_params.get(
        "start_plan_id"
    )  # Correct use of query_params
    end_plan_id = request.query_params.get("end_plan_id")

    if not start_plan_id or not end_plan_id:
        return Response(
            {"error": "Please provide both start and end plan IDs"}, status=400
        )

    try:
        # Filter the plans for the specific line and range
        plans = Plan.objects.filter(
            plan_id__gte=start_plan_id, plan_id__lte=end_plan_id, line=line_type
        )

        # Summarize the weights for the plans
        pulllist = (
            Weight.objects.filter(plan__in=plans)
            .values("component")
            .annotate(total_quantity=Sum("quantity"))
        )

        return Response(list(pulllist))

    except Exception as e:
        return Response({"error": str(e)}, status=500)
