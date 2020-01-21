from django import forms


class Compare_Form(forms.Form):
    key_word = forms.CharField(label='key_word', max_length=100)


class Search_Form(forms.Form):
    key_word = forms.CharField(label='key_word', max_length=100)
    CHOICES = [('Restrictiva', 'R'), ('Permisiva', 'P')]
    type = forms.CharField(label='Gender', widget=forms.RadioSelect(choices=CHOICES))


class Historical_Form(forms.Form):
    ean = forms.CharField(label='ean')
    name = forms.CharField(label='name')
    web = forms.CharField(label='web')
