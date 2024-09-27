from django.db import models

# Model for the Plan
class Plan(models.Model):
    plan_id = models.CharField(max_length=10, primary_key=True)  # Assuming the key is the unique plan ID
    batches = models.DecimalField(max_digits=10, decimal_places=2)
    progress = models.CharField(max_length=20, default="in-progress")  # In-progress, done, etc.
    order = models.IntegerField(default=-1)  # Order of the plan
    line = models.CharField(
        max_length=100, default="line"
    )  # Set a default value

    def __str__(self):
        return f"Plan {self.plan_id} - {self.line}"

# Model for Pages associated with each plan
class Page(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='pages')
    page_number = models.CharField(max_length=10)

    def __str__(self):
        return f"Page {self.page_number} for Plan {self.plan.plan_id}"

# Model for Weights associated with each plan
class Weight(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='weights')
    component = models.CharField(max_length=50)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.component}: {self.quantity} lbs for Plan {self.plan.plan_id}"
