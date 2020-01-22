from django import forms


class Compare_Form(forms.Form):
    key_word = forms.CharField(label='key_word', max_length=100)


class Search_Form(forms.Form):
    key_word = forms.CharField(label='key_word', max_length=100)
    CHOICES = [('Nivel 1', 'N1'), ('Nivel 2', 'N2'), ('Nivel 3', 'N3')]
    type = forms.CharField(label='Gender', widget=forms.RadioSelect(choices=CHOICES))


class Historical_Form(forms.Form):
    ean = forms.CharField(label='ean')
    name = forms.CharField(label='name')
    web = forms.CharField(label='web')
