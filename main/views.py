from django.shortcuts import render
from .forms import *
from .scrapping import *

# Create your views here.

#Index
def index(request):
    return render(request, "index.html")

#Search engine
def search(request):
    if request.method == 'POST':
        form = Search_Form(request.POST)
        if form.is_valid():
            print("Valor:")
            productName = form.cleaned_data['key_word']
            print(productName)
            return render(request, 'search_result.html', {'productName': productName})
    else:
        form = Search_Form()

    return render(request, 'index.html', {'form': form})

def compare(request):
    if request.method == 'GET':
        form = Search_Form()
        return render(request, 'compare_search.html', {'form': form})
    else:
        form = Search_Form(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key_word']
            extract_data_elCorteIngles(key)
