from django import forms

class Search_Form(forms.Form):
    key_word = forms.CharField(label='key_word', max_length=100)