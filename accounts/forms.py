from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""

    email = forms.EmailField(required=True)
    display_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "display_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "mt-1 block w-full rounded-md border-slate-300 shadow-sm "
                "focus:border-primary-500 focus:ring-primary-500 sm:text-sm "
                "px-3 py-2 border"
            )


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""

    class Meta:
        model = User
        fields = ("display_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "mt-1 block w-full rounded-md border-slate-300 shadow-sm "
                "focus:border-primary-500 focus:ring-primary-500 sm:text-sm "
                "px-3 py-2 border"
            )
