from django import forms
from django.contrib.auth.forms import AuthenticationForm


class RegisterForm(forms.Form):
    student_details = forms.FileField(label='Upload Student Details', required=False)
    teacher_details = forms.FileField(label='Upload Faculty  Details', required=False)

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'id': 'username',
        'name': 'username',
        'autocomplete': 'username',
        'class': 'form-control',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'id': 'password',
        'name': 'password',
        'autocomplete': 'current-password',
        'class': 'form-control',
    }))
