from django.contrib import admin
from.models import FailedPlan, Plan, Page, Weight, SortedPDF, PdfUpload

# Register your models here.
admin.site.register(Plan)
admin.site.register(Page)
admin.site.register(Weight)
admin.site.register(SortedPDF)
admin.site.register(PdfUpload)
admin.site.register(FailedPlan)
