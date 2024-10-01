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

    def __init__(
        self, weights_file=None, batches_file=None, can1=[], hydro=[], line3=[]
    ):
        # upload data
        self.weights_file = weights_file
        self.batches_file = batches_file
        self.can1 = can1
        self.hydro = hydro
        self.line3 = line3

        # dictionaries
        self.dictionary = {}  # Main dictionary to store plan data
        self.can1_dict = {}
        self.hydro_dict = {}
        self.line3_dict = {}

        # pull list
        self.pull_list = {}  # Dictionary to store aggregated rcode data

        # sortedpdf
        self.plans_in_order_pdf = None

        # error_plans
        self.error_plans = {}

        # enumberable for progress
        self.status = self.Status.IN_PROGRESS  # Initial status set to IN_PROGRESS

    def ensure_plan_key_exists(self, plan_key):
        """
        Ensure that a plan key exists in the dictionary.
        If not, initialize it with default values.
        """
        if plan_key not in self.dictionary:
            self.dictionary[plan_key] = {
                "pages": {},
                "weights": [],
                "batches": 0,
                "progress": self.status.value,
                "order": 0,
                "line": "",
            }

    # Modifier functions
    def complete_task(self):
        """Set the status of the plan to DONE."""
        self.status = self.Status.DONE

    def update_weights(self, plan_key, component_value, quantity_value):
        """Update the weights for a specific plan."""
        self.ensure_plan_key_exists(plan_key)
        self.dictionary[plan_key]["weights"].append({component_value: quantity_value})

    def update_front_page(self, plan_key, page_value):
        """Update the pages for a specific plan."""
        self.ensure_plan_key_exists(plan_key)
        self.dictionary[plan_key]["pages"]["front"] = page_value
    def update_back_page(self, plan_key, page_value):
        """Update the pages for a specific plan."""
        self.ensure_plan_key_exists(plan_key)
        self.dictionary[plan_key]["pages"]["back"] = page_value

    def update_batches(self, plan_key, batch_value):
        """Update the batch value for a specific plan."""
        self.ensure_plan_key_exists(plan_key)
        self.dictionary[plan_key]["batches"] = batch_value

    def extract_weights_plans_and_pages(self):
        """
        Extract plan numbers, pages, and weights from the weights PDF.
        Use regular expressions to identify and extract relevant information.
        """
        weights_plan_number_re = re.compile(r"^2\d{6}")  # Regex to find plan numbers
        weights_page_number_re = re.compile(
            r"(Page)\s\-\s([0-9]+)"
        )  # Regex to find page numbers
        component_pattern = re.compile(
            r"(?<=310\s(?:40\.00|75\.00)\s)(\w+)(?:/\d+)?"
        )  # Regex to find components
        quantity_pattern = re.compile(
            r"(\d+)(?=\.\d+\s*LB)"
        )  # Regex to find quantities

        with pdfplumber.open(self.weights_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()  # Extract text from each page
                for line in text.split("\n"):
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
                            self.update_back_page(found_plan, found_page)
                            found_page = None

                        # Extract and update weights if found
                        if component_match and quantity_match:
                            component_value = component_match.group()
                            quantity_value = quantity_match.group()
                            self.update_weights(
                                found_plan, component_value, quantity_value
                            )

    def extract_batches_plans_and_pages(self):
        """
        Extract plan numbers, pages, and batch totals from the batches PDF.
        Use regular expressions to identify and extract relevant information.
        """
        batches_plan_number_re = re.compile(r"(Production Plan)\s*:\s*([0-9]+)")
        batches_page_number_re = re.compile(r"(Page)\s*:\s*([0-9]+)")
        flex_list_re = re.compile(r"(Production Plan)(.*)(Pouch)")
        batch_number_re = re.compile(r"(?:Totals:\s*)([0-9]+\.?[0-9]*)")

        with pdfplumber.open(self.batches_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text = text.strip()  # Clean the extracted text
                    found_plan = None
                    found_page = None
                    for line in text.split("\n"):
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
                                self.update_front_page(found_plan, found_page)
                        if batch_total:
                            # Update batches if found_plan is not None
                            if found_plan:
                                self.update_batches(found_plan, batch_total.group(1))

    def read_pdfs(self):
        """Read the input PDF files."""
        self.weights_input_pdf = PdfReader(self.weights_file)
        self.batches_input_pdf = PdfReader(self.batches_file)

    def update_ordered_dict(self, items_list, line):
        """Update the ordered dictionary based on the item list and line type."""
        ordered_dict = {}
        for item in items_list:
            if item not in self.dictionary:
                continue
            # Update dictionary entries
            self.dictionary[item]["order"] = items_list.index(item) + 1
            self.dictionary[item]["line"] = line
            ordered_dict[item] = self.dictionary[item]
        return ordered_dict

    def order_dicts(self):
        """Process and update all the ordered dictionaries."""
        self.can1_dict = self.update_ordered_dict(self.can1, "can1")
        self.hydro_dict = self.update_ordered_dict(self.hydro, "hydro")
        self.line3_dict = self.update_ordered_dict(self.line3, "line3")

    def put_pages_together(self, items_list, items_dict, pdf_writer):
        """Find and add pages for the items in the given dictionary."""
        for item in items_list:
            try:
                # Get unique pages while preserving order
                # pages = list(dict.fromkeys(items_dict[item]["pages"]))
                front_page = int(items_dict[item]["pages"]["front"])
                back_page = int(items_dict[item]["pages"]["back"])
                if back_page is not None:
                    back = self.weights_input_pdf.pages[back_page+1]
                    pdf_writer.add_page(back)
                    front = self.batches_input_pdf.pages[front_page+1]
                    pdf_writer.add_page(front)
                    
            except (IndexError, KeyError) as e:
                self.error_plans[item] = items_dict.pop(item, None)
                print(f"Error processing item {item}: {e}")
                continue

    def process_data(self):
        """Add specific pages to a new PDF based on the ordered plans."""
        # Read PDF files
        self.read_pdfs()

        # Process dictionaries
        self.order_dicts()

        pdf_writer = PdfWriter()

        # Process each list and add pages to the PDF
        for items_list, items_dict in [
            (self.can1, self.can1_dict),
            (self.hydro, self.hydro_dict),
            (self.line3, self.line3_dict),
        ]:
            # Add a blank page as a separator
            pdf_writer.add_blank_page(width=792, height=612)
            self.put_pages_together(items_list, items_dict, pdf_writer)

        # Write the ordered pages to a new PDF file
        self.write_pdf(pdf_writer)

    def write_pdf(self, pdf_writer):
            """Write the collected pages to a new PDF file."""
            pdf_path = Path("/tmp/plans_in_order.pdf")  # Save the PDF to a temporary location
            with pdf_path.open(mode="wb") as output_file:
                pdf_writer.write(output_file)
            print(f"PDF written successfully to {pdf_path}")
            self.plans_in_order_pdf = pdf_path
# Example usage:


    def process_plan_sort(self):
        """
        Main function to process plan sorting.
        Reads order files, extracts plan data, and adds pages to the PDF.
        """
        # Extract plans and pages from PDFs
        self.extract_weights_plans_and_pages()
        self.extract_batches_plans_and_pages()

        # Add pages to a new PDF based on the extracted data
        self.process_data()
        # # Output the ordered dictionary as a JSON string
        # json_data = json.dumps(self.ordered_dict, indent=8)
        # print(json_data)


# Usage:
# pdf_plan_sorter = PdfPlanSorter()
# pdf_plan_sorter.process_plan_sort()  # Process the plan sorting
# pdf_plan_sorter.get_pull_list(pdf_plan_sorter.ordered_dict)  # Sum all rcodes
# # Print a header for the table
# print(f'{"R_CODE":<15} {"WEIGHT (LBS)"}')
# print("-" * 25)

# # Iterate through the items and print them in table format
# for key, value in pdf_plan_sorter.pull_list.items():
#     print(f"{key:<15} {value}")
