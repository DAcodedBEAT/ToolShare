from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from accounts.models import UserProfile
from django.forms import ModelForm

from accounts.models import Locations


class UserProfileCreateForm(ModelForm):
    """
    Creates form to create UserProfile.
    """

    class Meta:
        model = UserProfile
        fields = ('phone_number', 'pic')
        exclude = ('location',)
        widgets = {'phone_number': forms.TextInput(attrs={'placeholder': 'ex. 1234567890'})}

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if not phone.isalnum():
            raise ValidationError("Invalid Phone Number.")
        return phone


class UserProfileEditForm(ModelForm):
    """
    Creates form to edit UserProfile.
    """

    location = forms.ModelChoiceField(queryset=Locations.objects.none())

    def __init__(self, *args, **kwargs):
        super(UserProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = Locations.objects.filter(user=kwargs['instance'].user)

    class Meta:
        model = UserProfile
        fields = ('location', 'phone_number', 'pic')

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if not phone.isalnum():
            raise ValidationError("Invalid Phone Number.")
        return phone


class UserRegisterForm(UserCreationForm):
    """
    Creates form to register a user.
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class AddLocation(ModelForm):
    """
    Creates form to add a new location.
    """
    class Meta:
        model = Locations
        fields = ['address']
        exclude = ('loc_id', 'user', 'location', 'default')