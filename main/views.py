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
                Producto_ECI.objects.update_or_create(ean=str(prod["ean"]), nombre=str(prod["title"]), descripcion=str(prod["description"]), link=str(prod["link"]))
                Historico_ECI.objects.create(fecha=datetime.datetime.now(), producto_id=str(prod["ean"]), precio=str(prod["price"]))
                eci_ean.add(str(prod["ean"]))
            for prodM in mm:
                Producto_MM.objects.update_or_create(ean=str(prodM["ean"]), nombre=str(prodM["title"]), descripcion=str(prodM["description"]), link=str(prodM["link"]))
                Historico_MM.objects.create(fecha=datetime.datetime.now(), producto_id=str(prodM["ean"]), precio=str(prodM["price"]))
                mm_ean.add(str(prodM["ean"]))
            l = list(eci_ean & mm_ean)
            mostrar = False
            prod_eci = []
            prod_mm = []
            if len(l) > 0:
                mostrar = True
                for e in l:
                    prod_eci.append(Historico_ECI.objects.filter(producto_id=e).order_by("-fecha")[0])
                    prod_mm.append(Historico_MM.objects.filter(producto_id=e).order_by("-fecha")[0])
            return render(request, 'compare_result.html', {"eci": prod_eci, "mm": prod_mm, "productName": key, "mostrar": mostrar})
