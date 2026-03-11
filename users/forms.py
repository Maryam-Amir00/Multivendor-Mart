from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class VendorSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "vendor"
        user.is_approved = False
        if commit:
            user.save()
        return user


class CustomerSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "customer"
        user.is_approved = True
        if commit:
            user.save()
        return user
