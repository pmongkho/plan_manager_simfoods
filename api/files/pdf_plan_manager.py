import json
import re
from collections import defaultdict, OrderedDict
from pathlib import Path
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from enum import Enum

# Define a class to handle the PDF plan sorting
class PdfPlanSorter:
    # Nested enum class to track the status of a plan
    class Status(Enum):
        IN_PROGRESS = "in-progress"
        DONE = "done"

    def __init__(self):
        # Initialize file paths and dictionaries to store data
        self.weights_file_path = 'api/files/plan_weights.pdf'     #plan_weights.pdf
        self.batches_file_path = 'api/files/plan_batches.pdf'     #plan_batches.pdf
        self.can1 = []  # List to hold can1 plan numbers
        self.hydro = []  # List to hold hydro plan numbers
        self.line3 = []  # List to hold line3 plan numbers
        self.can1_dict = {}
        self.hydro_dict = {}
        self.line3_dict = {}
        self.ordered_dict = {}
        self.dictionary = {}  # Main dictionary to store plan data
        self.pull_list = {}  # Dictionary to store aggregated rcode data
        self.status = self.Status.IN_PROGRESS  # Initial status set to IN_PROGRESS

    def txt_to_array(self, file_path):
        """
        Read the contents of an order file and return a list of stripped lines.

        Parameters:
            file_path (str): The path to the order file.

        Returns:
            list: A list containing the stripped lines of the file.
        """
        orders = []
        seen = set()  # Set to track seen lines and avoid duplicates
        with open(file_path, "r") as order_file:
            for line in order_file:
                stripped_line = line.strip()
                if stripped_line not in seen:
                    seen.add(stripped_line)
                    orders.append(stripped_line)
        return orders

    def ensure_plan_key_exists(self, plan_key):
        """
        Ensure that a plan key exists in the dictionary.
        If not, initialize it with default values.
        """
        if plan_key not in self.dictionary:
            self.dictionary[plan_key] = {
                "pages": [],
                "weights": [],
                "batches": 0,
                "progress": self.status.value,
                "order": 0,
                 "line":"",
            }

    def complete_task(self):
        """Set the status of the plan to DONE."""
        self.status = self.Status.DONE

    def update_weights(self, plan_key, component_value, quantity_value):
        """Update the weights for a specific plan."""
        self.ensure_plan_key_exists(plan_key)
        self.dictionary[plan_key]["weights"].append({component_value: quantity_value})

    def update_pages(self, plan_key, page_values):
        """Update the pages for a specific plan."""
        self.ensure_plan_key_exists(plan_key)
        self.dictionary[plan_key]["pages"].extend(page_values)

    def update_batches(self, plan_key, batch_value):
        """Update the batch value for a specific plan."""
        self.ensure_plan_key_exists(plan_key)
        self.dictionary[plan_key]["batches"] = batch_value

    def extract_weights_plans_and_pages(self):
        """
        Extract plan numbers, pages, and weights from the weights PDF.
        Use regular expressions to identify and extract relevant information.
        """
        weights_plan_number_re = re.compile(r'^2\d{6}')  # Regex to find plan numbers
        weights_page_number_re = re.compile(r'(Page)\s\-\s([0-9]+)')  # Regex to find page numbers
        component_pattern = re.compile(r'(?<=310\s(?:40\.00|75\.00)\s)(\w+)(?:/\d+)?')  # Regex to find components
        quantity_pattern = re.compile(r'(\d+)(?=\.\d+\s*LB)')  # Regex to find quantities

        with pdfplumber.open(self.weights_file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()  # Extract text from each page
                for line in text.split('\n'):
                    page_match = weights_page_number_re.search(line)
                    plan_match = weights_plan_number_re.search(line)

                    # Match component and quantity in the line
                    component_match = component_pattern.search(line)
                    quantity_match = quantity_pattern.search(line)

                    if page_match:
                        found_page = page_match.group(2)
                    elif plan_match:
                        found_plan = plan_match.group()
                        if found_page:
                            self.update_pages(found_plan, [found_page])
                            found_page = None

                        # Extract and update weights if found
                        if component_match and quantity_match:
                            component_value = component_match.group()
                            quantity_value = quantity_match.group()
                            self.update_weights(found_plan, component_value, quantity_value)

    def extract_batches_plans_and_pages(self):
        """
        Extract plan numbers, pages, and batch totals from the batches PDF.
        Use regular expressions to identify and extract relevant information.
        """
        batches_plan_number_re = re.compile(r'(Production Plan)\s*:\s*([0-9]+)')
        batches_page_number_re = re.compile(r'(Page)\s*:\s*([0-9]+)')
        flex_list_re = re.compile(r'(Production Plan)(.*)(Pouch)')
        batch_number_re = re.compile(r'(?:Totals:\s*)([0-9]+\.?[0-9]*)')

        with pdfplumber.open(self.batches_file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text = text.strip()  # Clean the extracted text
                    found_plan = None
                    found_page = None
                    for line in text.split('\n'):
                        line = line.strip()  # Clean each line
                        # Check for flex plans and skip if found
                        flex_match = flex_list_re.search(line)
                        if flex_match:
                            continue
                        # Extract page and plan numbers
                        page_match = batches_page_number_re.search(line)
                        plan_match = batches_plan_number_re.search(line)
                        batch_total = batch_number_re.search(line)

                        if page_match:
                            found_page = page_match.group(2)
                        if plan_match:
                            found_plan = plan_match.group(2)
                            # Update pages if found_page is not None
                            if found_page:
                                self.update_pages(found_plan, [found_page])
                        if batch_total:
                            # Update batches if found_plan is not None
                            if found_plan:
                                self.update_batches(found_plan, batch_total.group(1))

    def add_pages_to_pdf(self):
        
        """Add specific pages to a new PDF based on the ordered plans."""
        weights_input_pdf = PdfReader(self.weights_file_path)
        batches_input_pdf = PdfReader(self.batches_file_path)
        pdf_writer = PdfWriter()

        # Helper function to update the ordered dictionary
        def update_ordered_dict(items_list, line):
            for item in items_list:
                if item not in self.dictionary:
                    continue
                # self.dictionary[item]["label"] = label
                self.dictionary[item]["order"] = items_list.index(item)+1
                self.dictionary[item]["line"]= line
                ordered_dict = {}
                ordered_dict[item] = self.dictionary[item]
            return ordered_dict

        # Update the ordered dictionary in the specified order
        self.can1_dict = update_ordered_dict(self.can1, "can1")
        self.hydro_dict = update_ordered_dict(self.hydro, "hydro")
        self.line3_dict = update_ordered_dict(self.line3, "line3")

        # Helper function to process items
        def find_and_add_pages(items_list, items_dict):
            for item in items_list:
                try:
                    # Get unique pages while preserving order
                    pages = list(dict.fromkeys(items_dict[item]["pages"]))
                    findpage2 = int(pages[1]) - 1 if len(pages) > 1 else None
                    findpage1 = int(pages[0]) - 1
                    if findpage2 is not None:
                        page2 = batches_input_pdf.pages[findpage2]
                        pdf_writer.add_page(page2)
                    page1 = weights_input_pdf.pages[findpage1]
                    pdf_writer.add_page(page1)
                except (IndexError, KeyError) as e:
                    print(f"Error processing item {item}: {e}")
                    continue

        # Process each list and add pages to the PDF
        for items_list in [self.can1, self.hydro, self.line3]:
            pdf_writer.add_blank_page(width=792, height=612)  # Add a blank page as a separator
            for dict in [self.can1_dict, self.hydro_dict, self.line3_dict]:
                find_and_add_pages(items_list, dict)

        # Write the ordered pages to a new PDF file
        with Path("plans_in_order.pdf").open(mode="wb") as output_file:
            pdf_writer.write(output_file)

    def get_pull_list(self, dictionary):
        """
        Sum the quantities for each rcode across all plans.
        """
        rcode_sums = {}

        for plan_key, plan_value in dictionary.items():
            for weight in plan_value['weights']:
                for rcode, value in weight.items():
                    if rcode not in rcode_sums and rcode.startswith('R') and not rcode.startswith('RN'):
                        rcode_sums[rcode] = 0
                        rcode_sums[rcode] += int(value)
        sorted_r_codes = dict(sorted(rcode_sums.items()))

        # Store the summed rcode values in the pull_list attribute
        self.pull_list = sorted_r_codes

    def process_plan_sort(self):
        """
        Main function to process plan sorting.
        Reads order files, extracts plan data, and adds pages to the PDF.
        """
        # Extract plans and pages from PDFs
        self.extract_weights_plans_and_pages()
        self.extract_batches_plans_and_pages()

        self.can1 = self.txt_to_array("api/files/order_can1.txt")
        self.hydro = self.txt_to_array("api/files/order_hydro.txt")
        self.line3 = self.txt_to_array("api/files/order_line3.txt")

        # Add pages to a new PDF based on the extracted data
        self.add_pages_to_pdf()
        # # Output the ordered dictionary as a JSON string
        json_data = json.dumps(self.ordered_dict, indent=8)
        print(json_data)

# Usage:
pdf_plan_sorter = PdfPlanSorter()
pdf_plan_sorter.process_plan_sort()  # Process the plan sorting
pdf_plan_sorter.get_pull_list(pdf_plan_sorter.ordered_dict)  # Sum all rcodes
# Print a header for the table
print(f'{"R_CODE":<15} {"WEIGHT (LBS)"}')
print('-' * 25)

# Iterate through the items and print them in table format
for key, value in pdf_plan_sorter.pull_list.items():
    print(f'{key:<15} {value}')