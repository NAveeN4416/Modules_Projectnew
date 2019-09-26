from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from datetime import date, datetime

def validate_gender(value=False):

	if value:
		return 'Male'

	return 'Female'


class UserRegistration(UserCreationForm):

	username   	 = forms.CharField(max_length='30',required=True,help_text='30 chars')
	first_name 	 = forms.CharField(max_length='30',required=True,help_text='30 chars')
	last_name  	 = forms.CharField(max_length='30',required=True,help_text='30 Chars')
	email      	 = forms.EmailField(max_length='30',required=True,help_text='30 Chars')
	phone_number = forms.CharField(max_length='10',required=True,help_text='10 Chars')
	password1  	 = forms.CharField(max_length='30',required=True,help_text='30 Chars', widget=forms.PasswordInput)
	password2  	 = forms.CharField(max_length='30',required=True,help_text='30 Chars', widget=forms.PasswordInput)

	#Set Attributes for tags
	username.widget.attrs.update({'class':'form-control','placeholder':'UserName *','minlength':'2'})
	first_name.widget.attrs.update({'class':'form-control','placeholder':'First Name *','minlength':'2'})
	last_name.widget.attrs.update({'class':'form-control','placeholder':'Last Name *'})
	email.widget.attrs.update({'class':'form-control','placeholder':'Your Email *'})
	phone_number.widget.attrs.update({'class':'form-control','placeholder':'Phone Number *','minlength':'10'})
	password1.widget.attrs.update({'class':'form-control','placeholder':'Password *'})
	password2.widget.attrs.update({'class':'form-control','placeholder':'Confirm Password *'})


	#Related the model to which form will save
	class Meta:
		model  = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


BIRTH_YEAR_CHOICES = ['1980', '1981', '1982']
FAVORITE_COLORS_CHOICES = [
							    ('blue', 'Blue'),
							    ('green', 'Green'),
							    ('black', 'Black'),
							]


class Forms_Demo(forms.Form):

	name  = forms.CharField(initial="eg: John",label="First Name",label_suffix="",max_length=10,help_text='10 Chars')
	email = forms.EmailField(label="Email Id",label_suffix="")
	image = forms.ImageField(label="Image",label_suffix="")
	dob   = forms.DateField(widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))
	favorite_colors = forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple,choices=FAVORITE_COLORS_CHOICES)
	date  = forms.DateField(input_formats=['%d-%m-%Y'],help_text="format - '23-09-2019'")