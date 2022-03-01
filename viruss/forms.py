from django import forms

class UploadFileForm(forms.Form):
    tittle = forms.CharField(max_length=500)
    file = forms.FileField
