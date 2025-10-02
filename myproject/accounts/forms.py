from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import UploadedFile
User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']        


class QnAUploadForm(forms.Form):
    file = forms.FileField(label="Upload your notes (PDF)")
    exam_level = forms.ChoiceField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    num_questions = forms.IntegerField(min_value=1)
    total_marks = forms.IntegerField(min_value=1)
    question_type = forms.ChoiceField(choices=[('objective', 'Objective'), ('subjective', 'Subjective'), ('both', 'Both')])

