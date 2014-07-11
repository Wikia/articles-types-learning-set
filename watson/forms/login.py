from django import forms


class WatsonLoginForm(forms.Form):
    user = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)