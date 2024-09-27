from django.shortcuts import render, redirect
from .forms import PdfUploadForm
from .models import Plan, Page, Weight
from .files.pdf_plan_manager import (
    PdfPlanSorter,
)  # Assuming you have PdfPlanSorter as a utility class for processing
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import authenticate, login, logout

# use loginrequired for the home view when using auth

def is_admin(user):
    return user.is_staff or user.is_superuser  # Adjust based on your admin criteria


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")  # Redirect to the home page or dashboard
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    else:
        return render(request, "login.html")


@user_passes_test(
    is_admin, login_url="dashboard"
)  # Redirect non-admins to the dashboard
def upload_view(request):
    if request.method == "POST":
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Retrieve the uploaded files
            weights_file = request.FILES["weights_file"]
            batches_file = request.FILES["batches_file"]
            # can1 = request.FILES['can1']
            # hydro = request.FILES['hydro']
            # line3 = request.FILES['line3_file']
            can1 = form.cleaned_data["can1"]
            hydro = form.cleaned_data["hydro"]
            line3 = form.cleaned_data["line3"]

            # Save files to the filesystem or a temporary directory
            weights_file_path = "/tmp/" + weights_file.name
            batches_file_path = "/tmp/" + batches_file.name
            # can1_file_path = '/tmp/' + can1.name
            # hydro_file_path = '/tmp/' + hydro.name
            # line3_file_path = '/tmp/' + line3.name

            with open(weights_file_path, "wb+") as destination:
                for chunk in weights_file.chunks():
                    destination.write(chunk)

            with open(batches_file_path, "wb+") as destination:
                for chunk in batches_file.chunks():
                    destination.write(chunk)

            # with open(can1_file_path, 'wb+') as destination:
            #     for chunk in can1_file.chunks():
            #         destination.write(chunk)

            # with open(hydro_file_path, 'wb+') as destination:
            #     for chunk in hydro_file.chunks():
            #         destination.write(chunk)

            # with open(line3_file_path, 'wb+') as destination:
            #     for chunk in line3_file.chunks():
            #         destination.write(chunk)

            # Convert the form data into lists
            can1_list = can1.splitlines()  # Splits the input by lines
            hydro_list = hydro.splitlines()  # Splits the input by lines
            line3_list = line3.splitlines()  # Splits the input by lines

            # Initialize and run PdfPlanSorter with the file paths
            pdf_plan_sorter = PdfPlanSorter(
                weights_file=weights_file,
                batches_file=batches_file,
                can1=can1_list,
                hydro=hydro_list,
                line3=line3_list,
            )
            # pdf_plan_sorter.weights_file_path = weights_file_path
            # pdf_plan_sorter.batches_file_path = batches_file_path

            # Process the text files and convert them to lists
            # can1_list = pdf_plan_sorter.txt_to_array(can1_file_path)
            # hydro_list = pdf_plan_sorter.txt_to_array(hydro_file_path)
            # line3_list = pdf_plan_sorter.txt_to_array(line3_file_path)

            # Process the PDFs and save to the database
            pdf_plan_sorter.process_plan_sort()  # Extract and process plans from PDFs

            # Save each plan, page, and weight to the database
        # Iterate over each dictionary one by one
    for plan_dict in [
        pdf_plan_sorter.can1_dict,
        pdf_plan_sorter.hydro_dict,
        pdf_plan_sorter.line3_dict,
    ]:
        for plan_id, plan_data in plan_dict.items():
            plan_obj, created = Plan.objects.get_or_create(
                plan_id=plan_id,
                defaults={
                    "batches": plan_data["batches"],
                    "progress": plan_data["progress"],
                    "order": plan_data["order"],
                    "line": plan_data["line"],
                },
            )

            # Save pages
            for page_number in plan_data["pages"]:
                Page.objects.create(plan=plan_obj, page_number=int(page_number))

            # Save weights
            for weight in plan_data["weights"]:
                for component, quantity in weight.items():
                    Weight.objects.create(
                        plan=plan_obj, component=component, quantity=int(quantity)
                    )

        return redirect("dashboard")  # Redirect to a success page after processing

    else:
        form = PdfUploadForm()

    return render(request, "upload.html", {"form": form})


def dashboard_view(request):
    return render(request, "dashboard.html")


def home_view(request):
    form = PdfUploadForm()  # Initialize the form
    return render(request, "home.html")  # Pass the form to the template


def logout_view(request):
    logout(request)
    return redirect("login")  # Redirect to the login page after logging out
