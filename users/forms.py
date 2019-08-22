from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

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
