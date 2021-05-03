from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# create a form for the user to sign up
class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
	    model = User
	    fields = ["username", "email", "password1", "password2"]