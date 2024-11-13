import os
from django.db import models
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from api.files.pdf_plan_manager import PdfPlanSorter
from django.conf import settings
from django.contrib.postgres.fields import JSONField  # For PostgreSQL

# Model for the Plan
class Plan(models.Model):
    plan_id = models.CharField(max_length=10, primary_key=True)  # Assuming the key is the unique plan ID
    batches = models.DecimalField(max_digits=10, decimal_places=2)
    progress = models.CharField(max_length=20, default="in-progress")  # In-progress, done, etc.
    order = models.IntegerField(default=-1)  # Order of the plan
    line = models.CharField(
        max_length=100, default="line"
    )  # Set a default value
    created_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        # Manually delete associated objects
        PdfUpload.objects.all().delete()  # If no FK relation but you need cleanup
        SortedPDF.objects.all().delete()  # Clean up sorted PDFs
        FailedPlan.objects.all().delete()  # Delete failed plans

        super(Plan, self).delete(*args, **kwargs)  # Call the default delete method

    class Meta:
        ordering = ['order']  # Default ordering by `order` field


    def __str__(self):
        return f"Plan {self.plan_id}: {self.line}"


# Model for Pages associated with each plan
class Page(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="pages")
    front_page = models.CharField(max_length=10, null=True, blank=True)
    back_page = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"Front: {self.front_page}, Back: {self.back_page} for Plan {self.plan.plan_id}"


# Model for Weights associated with each plan
class Weight(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='weights')
    component = models.CharField(max_length=50)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.component}: {self.quantity} lbs for Plan {self.plan.plan_id}"

class SortedPDF(models.Model):
    pdf_file = models.FileField(upload_to="pdfs/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PDF created on {self.created_at}"


class PdfUpload(models.Model):
    weights_file = models.FileField(upload_to="uploads/")
    batches_file = models.FileField(upload_to="uploads/")
    can1 = models.TextField()  # Store the Can1 plan numbers
    hydro = models.TextField()  # Store the Hydro plan numbers
    line3 = models.TextField()  # Store the Line3 plan numbers
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp of the upload

    def __str__(self):
        return f"PDF Upload at {self.uploaded_at}"

    def save(self, *args, **kwargs):
        # Call the original save method to ensure the upload gets saved
        super().save(*args, **kwargs)

        # Call the upload processing logic after saving the instance
        self.process_upload()

    def process_upload(self):
        # Convert the form data into lists
        can1_list = self.can1.splitlines()
        hydro_list = self.hydro.splitlines()
        line3_list = self.line3.splitlines()

        # Initialize and run PdfPlanSorter with the file paths
        pdf_plan_sorter = PdfPlanSorter(
            weights_file=self.weights_file.path,
            batches_file=self.batches_file.path,
            can1=can1_list,
            hydro=hydro_list,
            line3=line3_list,
        )

        # Process the PDFs and extract plans
        pdf_plan_sorter.process_plan_sort()

        # Save each plan, page, and weight to the database
        for plan_dict in [
            pdf_plan_sorter.can1_dict,
            pdf_plan_sorter.hydro_dict,
            pdf_plan_sorter.line3_dict,
        ]:
            for plan_id, plan_data in plan_dict.items():
                try:
                    # Try to create the Plan object
                    plan_obj, created = Plan.objects.get_or_create(
                        plan_id=plan_id,
                        defaults={
                            "batches": plan_data.get("batches"),
                            "progress": plan_data.get("progress"),
                            "order": plan_data.get("order"),
                            "line": plan_data.get("line"),
                        },
                    )

                    # Assuming plan_data["pages"] is a dictionary like: {"front": 45, "back": 46}
                    pages_data = plan_data.get("pages", {})
                    front_page = pages_data.get("front")
                    back_page = pages_data.get("back")

                    # Create the Page object with both front and back pages
                    Page.objects.create(
                        plan=plan_obj,
                        front_page=str(front_page) if front_page else None,
                        back_page=str(back_page) if back_page else None,
                    )

                    # Save weights
                    for weight in plan_data["weights"]:
                        for component, quantity in weight.items():
                            Weight.objects.create(
                                plan=plan_obj,
                                component=component,
                                quantity=int(quantity),
                            )

                except Exception as e:
                    # Skip error handling here since `error_plans` will handle it
                    continue

        # **Process and Save Error Plans**
        # Loop over the error plans captured by `PdfPlanSorter`
        for plan_id, error_plan in pdf_plan_sorter.error_plans.items():
            FailedPlan.objects.create(
                plan_id=plan_id,
                batches=error_plan.get("batches", None),
                progress=error_plan.get("progress", "in-progress"),
                order=error_plan.get("order", -1),
                line=error_plan.get("line", "line"),
                error_details="Automatically captured from PdfPlanSorter"
            )

        # Save the sorted PDF to the `MEDIA_ROOT` directory
        with open(pdf_plan_sorter.plans_in_order_pdf, "rb") as pdf_file:
            # Instead of reading the file and saving the path, save it directly using the File object
            django_file = ContentFile(pdf_file.read())

            # Generate a unique file name under the sorted_pdfs directory
            file_name = default_storage.save("sorted_pdfs/plans_in_order.pdf", django_file)

            # Create and save the SortedPDF instance using the FileField
            sorted_pdf = SortedPDF.objects.create(pdf_file=file_name)
            sorted_pdf.save()


class FailedPlan(models.Model):
    plan_id = models.CharField(max_length=10)
    batches = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    progress = models.CharField(
        max_length=20, default="in-progress", null=True, blank=True
    )
    order = models.IntegerField(default=-1)
    line = models.CharField(max_length=100, default="line", null=True, blank=True)
    error_details = (
        models.TextField()
    )  # To store details of why this plan failed to be processed
    pages = models.JSONField(null=True, blank=True)  # Use django.db.models.JSONField
    weights = models.JSONField(null=True, blank=True)  # Use django.db.models.JSONField
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Failed Plan {self.plan_id} - Error: {self.error_details}"
