from django import forms

class Search_Form(forms.Form):
    key_word = forms.CharField(label='key_word', max_length=100)
    
class Historical_Form(forms.Form):
    ean = forms.CharField(label='ean')
    name = forms.CharField(label='name')
    web = forms.CharField(label='web')