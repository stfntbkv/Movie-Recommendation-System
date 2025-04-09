from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Rating


class RegistrationForm(UserCreationForm):
    """
    A form for user registration extending Django's built-in UserCreationForm.

    Attributes:
        email (EmailField): A required field for user email with validation.

    """
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        """
        Meta:
            model (User): Uses Django's User model.
            fields (tuple): Specifies the fields included in the form (username, email, password1, password2).
        """
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class RatingForm(forms.ModelForm):
    """
    A form for submitting movie ratings.
    """

    class Meta:
        """
        Meta:
            model (Rating): Uses the Rating model.
            fields (list): Specifies that only the 'rating' field is included in the form.
            widgets (dict): Defines the input type and attributes for the rating field.
            labels (dict): Provides a user-friendly label for the rating field.
        """
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 10, 'class': 'form-control'}),
        }
        labels = {
            'rating': 'Your Rating (1-10)',
        }
