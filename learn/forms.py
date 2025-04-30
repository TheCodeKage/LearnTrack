from django import forms
from django.core.validators import FileExtensionValidator

from .models import PDFMaterial, URLMaterial, Lecture


class URLMaterialForm(forms.ModelForm):
    class Meta:
        model = URLMaterial
        fields = ['name', 'url']


class PDFMaterialForm(forms.ModelForm):
    class Meta:
        model = PDFMaterial
        fields = ['name', 'file']


class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['name', 'content']


class StudyMaterialForm(forms.Form):
    name = forms.CharField()
    url = forms.URLField(required=False)
    file = forms.FileField(required=False, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

    def is_valid(self):
        valid = super().is_valid()
        if not self.url and not self.file:
            raise forms.ValidationError('URL or file is required')
        if self.url and self.file:
            raise forms.ValidationError('Only URL or file is required, Not both')
        return valid