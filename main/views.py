from django.shortcuts import render
from .forms import *
from .scrapping import *
from .models import *
import datetime


# Create your views here.

# Index
def index(request):
    return render(request, "index.html")


# Search engine
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
            eci = extract_data_elCorteIngles(key)
            mm = extract_data_mediaMarkt(key)
            eci_ean = set()
            mm_ean = set()
            for prod in eci:
                Producto_ECI.objects.update_or_create(ean=prod["ean"], nombre=prod["title"],
                                                      descripcion=prod["description"], link=prod["link"])
                Historico_ECI.objects.create(fecha=datetime.datetime.now(), producto_id=prod["ean"],
                                             precio=prod["price"])
                eci_ean.add(prod["ean"])
            for prodM in mm:
                Producto_MM.objects.update_or_create(ean=prodM["ean"], nombre=prodM["title"],
                                                     descripcion=prodM["description"], link=prodM["link"])
                Historico_MM.objects.create(fecha=datetime.datetime.now(), producto_id=prodM["ean"],
                                            precio=prodM["price"])
                mm_ean.add(prodM["ean"])
            res = list(eci_ean & mm_ean)[0]
            mostrar = False
            if res is not None:
                mostrar = True
            return render(request, 'compare_result.html', {"eci": Historico_ECI.objects.filter(producto_id=res).order_by("-fecha")[0],
                                                           "mm": Historico_MM.objects.filter(producto_id=res).order_by("-fecha")[0],
                                                           "productName": key, "mostrar": mostrar})
