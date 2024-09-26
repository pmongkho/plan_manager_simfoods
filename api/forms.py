from django import forms

class PdfUploadForm(forms.Form):
    weights_file = forms.FileField(label="Upload Weights PDF")
    batches_file = forms.FileField(label="Upload Batches PDF")
    can1 = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), label="Can1 Plan Numbers")
    hydro = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), label="Hydro Plan Numbers")
    line3 = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), label="Line3 Plan Numbers")
