# api/views.py

import os, re
import pdfplumber
from rest_framework.response import Response  # Use DRF's Response
from django.shortcuts import render
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
    ListAPIView,
)
from rest_framework import status
from .models import FailedPlan, Page, Plan, Weight
from .serializers import FailedPlanSerializer, PdfUploadSerializer, PlanSerializer
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.conf import settings
from collections import defaultdict

# Regex patterns to match component IDs and quantities
component_pattern = re.compile(r"(?<=310\s(?:40\.00|75\.00)\s)(\w+)(?:/\d+)?")
quantity_pattern = re.compile(r"(\d+)(?=\.\d+\s*LB)")

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from .models import PdfUpload, Plan, Page, Weight, FailedPlan, SortedPDF
from .serializers import PdfUploadSerializer
from django.db import transaction


class AdminManageDBView(CreateAPIView):
    serializer_class = PdfUploadSerializer
    # permission_classes = [IsAdminUser]  # Restrict to admin users

    # def perform_create(self, serializer):
    #     # Save and process the PDF upload, which includes processing the files
    #     serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the upload data
            pdf_upload = serializer.save()

            # Process the uploaded data
            pdf_upload.process_upload()

            return Response(
                {"message": "Upload and processing successful"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClearDatabaseView(APIView):
    # permission_classes = [IsAdminUser]  # Only admin access

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        # Clear relevant models
        Plan.objects.all().delete()
        Page.objects.all().delete()
        Weight.objects.all().delete()
        FailedPlan.objects.all().delete()
        SortedPDF.objects.all().delete()
        PdfUpload.objects.all().delete()

        return Response(
            {"message": "Database cleared successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


def extract_weights(pdf_file):
    weights = defaultdict(float)  # Dictionary to sum weights for each component

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for line in text.split("\n"):
                # Find all component and quantity matches within each line
                component_matches = component_pattern.findall(line)
                quantity_matches = quantity_pattern.findall(line)

                # Sum each component with its corresponding quantity if both exist
                for component, quantity in zip(component_matches, quantity_matches):
                    weights[component] += float(
                        quantity
                    )  # Add quantity to the component's total

    return weights


@csrf_exempt
def upload_weights_pdf(request):
    if request.method == "POST" and "pdf_file" in request.FILES:
        pdf_file = request.FILES["pdf_file"]  # Read the file directly from the request
        weights = extract_weights(pdf_file)
        return JsonResponse(weights)
    return JsonResponse({"error": "Invalid request"}, status=400)


class PlanListCreateView(ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdminUser]


class PlanDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    lookup_field = "pk"


class UploadPdfView(CreateAPIView):
    serializer_class = PdfUploadSerializer

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {"message": "Upload and processing successful"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FailedPlanListView(ListAPIView):
    queryset = FailedPlan.objects.all()
    serializer_class = FailedPlanSerializer


@api_view(["PUT"])
def update_plan_order(request):
    plans_data = request.data.get("plans", [])
    for plan_data in plans_data:
        plan_id = plan_data.get("plan_id")
        order = plan_data.get("order")
        if plan_id is not None and order is not None:
            Plan.objects.filter(plan_id=plan_id).update(order=order)
    return Response({"message": "Order updated successfully."}, status=200)


def index(request):
    return render(request, "index.html")


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
        plans = Plan.objects.filter(line=line_type)
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

        return Response(response_data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
