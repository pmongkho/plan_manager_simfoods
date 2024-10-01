# api/serializers.py

from rest_framework import serializers
from .models import FailedPlan, PdfUpload, Plan, Page, Weight


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["front_page", "back_page"]


class WeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weight
        fields = ["component", "quantity"]


class PlanSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True)  # Nested serializer for related pages
    weights = WeightSerializer(many=True)  # Nested serializer for related weights

    class Meta:
        model = Plan
        fields = ["plan_id", "batches", "progress", "order", "line", "pages", "weights"]

    def create(self, validated_data):
        pages_data = validated_data.pop("pages")
        weights_data = validated_data.pop("weights")
        plan = Plan.objects.create(**validated_data)

    # Use a set or check to prevent duplicate pages
        created_pages = set()

        # Create each page, ensuring no duplicates are created
        for page_data in pages_data:
            page_key = (page_data.get("front_page"), page_data.get("back_page"))
            if page_key not in created_pages:
                Page.objects.create(plan=plan, **page_data)
                created_pages.add(page_key)

        for weight_data in weights_data:
            Weight.objects.create(plan=plan, **weight_data)

        return plan

class PdfUploadSerializer(serializers.Serializer):
    class Meta:
        model = PdfUpload
        fields = ["weights_file", "batches_file", "can1", "hydro", "line3"]


class FailedPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailedPlan
        fields = "__all__"  # Or you can specify individual fields: ['plan_id', 'batches', 'progress', etc.]
