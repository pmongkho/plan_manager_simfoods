# api/serializers.py

from rest_framework import serializers
from .models import FailedPlan, PdfUpload, Plan, Page, Weight
from .files.pdf_plan_manager import PdfPlanSorter
import tempfile


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

    def update(self, instance, validated_data):
        # Update main fields of Plan
        instance.plan_id = validated_data.get("plan_id", instance.plan_id)
        instance.batches = validated_data.get("batches", instance.batches)
        instance.progress = validated_data.get("progress", instance.progress)
        instance.order = validated_data.get("order", instance.order)
        instance.line = validated_data.get("line", instance.line)
        instance.save()

        # Handle nested `pages`
        pages_data = validated_data.pop("pages", [])
        existing_page_ids = {page.id for page in instance.pages.all()}

        for page_data in pages_data:
            page_id = page_data.get("id")
            if page_id and page_id in existing_page_ids:
                # Update existing page
                page = Page.objects.get(id=page_id, plan=instance)
                page.front_page = page_data.get("front_page", page.front_page)
                page.back_page = page_data.get("back_page", page.back_page)
                page.save()
                existing_page_ids.remove(page_id)
            else:
                # Create new page if it doesn't exist
                Page.objects.create(plan=instance, **page_data)

        # Delete pages that are not in the updated data
        Page.objects.filter(id__in=existing_page_ids).delete()

        # Handle nested `weights`
        weights_data = validated_data.pop("weights", [])
        existing_weight_ids = {weight.id for weight in instance.weights.all()}

        for weight_data in weights_data:
            weight_id = weight_data.get("id")
            if weight_id and weight_id in existing_weight_ids:
                # Update existing weight
                weight = Weight.objects.get(id=weight_id, plan=instance)
                weight.component = weight_data.get("component", weight.component)
                weight.quantity = weight_data.get("quantity", weight.quantity)
                weight.save()
                existing_weight_ids.remove(weight_id)
            else:
                # Create new weight if it doesn't exist
                Weight.objects.create(plan=instance, **weight_data)

        # Delete weights that are not in the updated data
        Weight.objects.filter(id__in=existing_weight_ids).delete()

        return instance


class PdfUploadSerializer(serializers.Serializer):
    weights_file = serializers.FileField()
    batches_file = serializers.FileField()
    can1 = serializers.CharField()
    hydro = serializers.CharField()
    line3 = serializers.CharField()

    def create(self, validated_data):
        # Save weights and batches files to temporary files
        with tempfile.NamedTemporaryFile(
            delete=False
        ) as weights_tmp, tempfile.NamedTemporaryFile(delete=False) as batches_tmp:

            # Write the contents of each uploaded file to the temp file
            weights_tmp.write(validated_data["weights_file"].read())
            batches_tmp.write(validated_data["batches_file"].read())

            # Close files to flush content to disk
            weights_tmp.close()
            batches_tmp.close()

            # Convert the newline-separated strings to lists
            can1_list = validated_data["can1"].splitlines()
            hydro_list = validated_data["hydro"].splitlines()
            line3_list = validated_data["line3"].splitlines()

            # Initialize and run PdfPlanSorter with the temporary file paths
            pdf_plan_sorter = PdfPlanSorter(
                weights_file=weights_tmp.name,
                batches_file=batches_tmp.name,
                can1=can1_list,
                hydro=hydro_list,
                line3=line3_list,
            )

            # Run the processing
            pdf_plan_sorter.process_plan_sort()

        return PdfUpload.objects.create(
            weights_file=validated_data["weights_file"],
            batches_file=validated_data["batches_file"],
            can1=validated_data["can1"],
            hydro=validated_data["hydro"],
            line3=validated_data["line3"],
        )

        return validated_data  # Optionally, return what was processed if necessary


class FailedPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailedPlan
        fields = "__all__"  # Or you can specify individual fields: ['plan_id', 'batches', 'progress', etc.]
