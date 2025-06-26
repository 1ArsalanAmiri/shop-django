from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core import validators
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from . import models
from django.contrib.auth.forms import UserCreationForm


# class SignUpForm(forms.Form):
#
#     name = forms.CharField(max_length=100)
#     last_name = forms.CharField(max_length=100)
#     email = forms.EmailField()
#     password1 = forms.CharField(min_length=8 ,max_length=255,widget=forms.PasswordInput())
#     password2 = forms.CharField(min_length=8 ,max_length=255,widget=forms.PasswordInput())
#     phone_number = PhoneNumberField()
#
#
#     # phone = forms.CharField(max_length=255 , validators = [
#     #                                                         validators.RegexValidator(r'^(\+98|09|9)?9\d{9}$'),
#     #                                                         validators.MinLengthValidator(5),
#     #                                                         validators.MaxLengthValidator(20),])
#
#
#
#
#     def clean_name(self):
#         if self.data['name'] == self.data['password1']:
#             raise ValidationError("The name and the passwords cant be same")
#
#
#         return self.cleaned_data['name']


class SignUpForm(UserCreationForm):
    class Meta:
        model = models.User
        exclude = ['is staff' , 'is_active' , 'is_superuser','date_joined',
                   'last_login', 'groups', 'user_permissions','avatar' , 'address', 'password' , 'is_staff' ]
        # fields = ('first_name','last_name','email', 'phone_number')
        # fields = "__all__"


