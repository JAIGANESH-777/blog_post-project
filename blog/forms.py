from django import forms
from django.contrib.auth.models import User

class contactform(forms.Form):
    name=forms.CharField(label="Name",max_length=100,required=True)
    email=forms.EmailField(label="Email",required=True)
    message=forms.CharField(label="Message",required=True)

class RegisterForm(forms.Form):
    username=forms.CharField(label="Username",max_length=100,required=True)
    password=forms.CharField(label="Password",required=True)
    confirm_password=forms.CharField(label="Confrim Password",required=True)
    email=forms.EmailField(label="Email",required=True)

    class Meta:
        model=User
        fields=['username','email','password']