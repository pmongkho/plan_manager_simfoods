from django.shortcuts import render, redirect
from .forms import PdfUploadForm
from .models import Plan, Page, Weight
from .files.pdf_plan_manager import PdfPlanSorter  # Assuming you have PdfPlanSorter as a utility class for processing

def upload_and_process_files(request):
    if request.method == 'POST':
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Retrieve the uploaded files
            weights_file = request.FILES['weights_file']
            batches_file = request.FILES['batches_file']
            can1_file = request.FILES['can1_file']
            hydro_file = request.FILES['hydro_file']
            line3_file = request.FILES['line3_file']

            # Save files to the filesystem or a temporary directory
            weights_file_path = '/tmp/' + weights_file.name
            batches_file_path = '/tmp/' + batches_file.name
            can1_file_path = '/tmp/' + can1_file.name
            hydro_file_path = '/tmp/' + hydro_file.name
            line3_file_path = '/tmp/' + line3_file.name

            with open(weights_file_path, 'wb+') as destination:
                for chunk in weights_file.chunks():
                    destination.write(chunk)

            with open(batches_file_path, 'wb+') as destination:
                for chunk in batches_file.chunks():
                    destination.write(chunk)

            with open(can1_file_path, 'wb+') as destination:
                for chunk in can1_file.chunks():
                    destination.write(chunk)

            with open(hydro_file_path, 'wb+') as destination:
                for chunk in hydro_file.chunks():
                    destination.write(chunk)

            with open(line3_file_path, 'wb+') as destination:
                for chunk in line3_file.chunks():
                    destination.write(chunk)

            # Initialize and run PdfPlanSorter with the file paths
            pdf_plan_sorter = PdfPlanSorter()
            pdf_plan_sorter.weights_file_path = weights_file_path
            pdf_plan_sorter.batches_file_path = batches_file_path

            # Process the text files and convert them to lists
            can1_list = pdf_plan_sorter.txt_to_array(can1_file_path)
            hydro_list = pdf_plan_sorter.txt_to_array(hydro_file_path)
            line3_list = pdf_plan_sorter.txt_to_array(line3_file_path)

            # Process the PDFs and save to the database
            pdf_plan_sorter.process_plan_sort()  # Extract and process plans from PDFs

            # Save each plan, page, and weight to the database
            for plan_id, plan_data in pdf_plan_sorter.ordered_dict.items():
                plan_obj, created = Plan.objects.get_or_create(
                    plan_id=plan_id,
                    defaults={
                        'batches': plan_data['batches'],
                        'progress': plan_data['progress'],
                        'label': plan_data['label'],
                    }
                )

                # Save pages
                for page_number in plan_data['pages']:
                    Page.objects.create(plan=plan_obj, page_number=int(page_number))

                # Save weights
                for weight in plan_data['weights']:
                    for component, quantity in weight.items():
                        Weight.objects.create(plan=plan_obj, component=component, quantity=int(quantity))

            return redirect('success_url')  # Redirect to a success page after processing

    else:
        form = PdfUploadForm()

    return render(request, 'pdf_sorter/upload.html', {'form': form})
