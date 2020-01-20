from django.shortcuts import render
from .forms import *
from .scrapping import *
from .models import *
import datetime
import os
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup, AndGroup

dirindex = "main/index"

# Index
def index(request):
    return render(request, "index.html")


# Search engine
def search(request):
    if request.method == 'POST':
        form = Search_Form(request.POST)
        if form.is_valid():
            if not aux_check_index():
                aux_reset_all()
            key = form.cleaned_data['key_word']
            ix = open_dir(dirindex)
            with ix.searcher() as searcher:
                query = MultifieldParser(['descripcionECI', 'descripcionMM'], ix.schema).parse(key)
                results = searcher.search(query)
    else:
        form = Search_Form()

    return render(request, 'search.html', {'form': form})


def compare(request):
    if request.method == 'GET':
        form = Search_Form()
        return render(request, 'index.html', {'form': form})
    else:
        form = Search_Form(request.POST)
        if form.is_valid():
            if not aux_check_index():
                aux_reset_all()
            key = form.cleaned_data['key_word']
            eci = extract_data_elCorteIngles(key)
            mm = extract_data_mediaMarkt(key)
            eci_ean = set()
            mm_ean = set()
            for prod in eci:
                num_results = Producto_ECI.objects.filter(ean = str(prod["ean"])).count()
                if num_results == 0:
                    Producto_ECI.objects.create(ean=str(prod["ean"]), nombre=str(prod["title"]), descripcion=str(prod["description"]), link=str(prod["link"]))
                else:
                    Producto_ECI.objects.filter(ean = str(prod["ean"])).update(nombre=str(prod["title"]), descripcion=str(prod["description"]), link=str(prod["link"]))
                historico = Historico_ECI.objects.filter(producto_id=prod["ean"]).order_by("-fecha")

                #We check if is not void
                if len(historico)>0:
                    #We check if the price changed
                    if historico[0].precio!= prod["price"]:
                        Historico_ECI.objects.create(fecha=datetime.datetime.now(), producto_id=str(prod["ean"]), precio=str(prod["price"]))
                else:
                    Historico_ECI.objects.create(fecha=datetime.datetime.now(), producto_id=str(prod["ean"]), precio=str(prod["price"]))
                eci_ean.add(str(prod["ean"]))
            for prodM in mm:
                num_results = Producto_MM.objects.filter(ean = str(prodM["ean"])).count()
                if num_results == 0:
                    Producto_MM.objects.create(ean=str(prodM["ean"]), nombre=str(prodM["title"]), descripcion=str(prodM["description"]), link=str(prodM["link"]))
                else:
                    Producto_MM.objects.filter(ean = str(prod["ean"])).update(nombre=str(prodM["title"]), descripcion=str(prodM["description"]), link=str(prodM["link"]))
                historico = Historico_MM.objects.filter(producto_id=prodM["ean"]).order_by("-fecha")

                #We check if is not void
                if len(historico)>0:
                    #We check if the price changed
                    if historico[0].precio!= prodM["price"]:
                        Historico_MM.objects.create(fecha=datetime.datetime.now(), producto_id=str(prodM["ean"]), precio=str(prodM["price"]))
                else:
                    Historico_MM.objects.create(fecha=datetime.datetime.now(), producto_id=str(prodM["ean"]), precio=str(prodM["price"]))
                mm_ean.add(str(prodM["ean"]))
            l = list(eci_ean & mm_ean)
            mostrar = False
            prod_eci = []
            prod_mm = []
            if len(l) > 0:
                ix = open_dir(dirindex)
                writer = ix.writer()
                mostrar = True
                for e in l:
                    eci = Historico_ECI.objects.filter(producto_id=e).order_by("-fecha")[0]
                    mm = Historico_MM.objects.filter(producto_id=e).order_by("-fecha")[0]
                    add_doc(writer, e, mm.producto.descripcion, eci.producto.descripcion)
                    prod_eci.append(eci)
                    prod_mm.append(mm)
                writer.commit()
            return render(request, 'compare_result.html', {"eci": prod_eci, "mm": prod_mm, "productName": key, "mostrar": mostrar})


def historial_price(request):
    form = Historical_Form(request.GET)
    key = form['ean'].value()
    name = form['name'].value()
    web = form['web'].value()
    if web=='eci':
        res = Historico_ECI.objects.filter(producto_id=key).order_by("-fecha")
        shop = "El Corte Ingles"
        color = "darkgreen"
    elif web == 'mm':
        res = Historico_MM.objects.filter(producto_id=key).order_by("-fecha")
        shop = "Media Markt"
        color = "red"
    return render(request, 'historial_price.html', {"res": res,"name": name, 'shop':shop, 'color':color})

def reset_all(request):
    aux_reset_all()
    return render(request, "index.html")


# Métodos auxiliares

def aux_reset_all():
    aux_reset_bd()
    aux_reset_index()

def aux_reset_index():
    if not os.path.exists(dirindex):
        os.mkdir(dirindex)
    ix = create_in(dirindex, schema=Schema(ean=NUMERIC(int, 64, stored=True), descripcionMM=TEXT(stored=True), descripcionECI=TEXT(stored=True)))
    writer = ix.writer()
    writer.commit()


def aux_reset_bd():
    Producto_ECI.objects.all().delete()
    Producto_MM.objects.all().delete()
    Historico_ECI.objects.all().delete()
    Historico_MM.objects.all().delete()


def aux_check_index():
    check = True
    if not os.path.exists(dirindex):
        os.mkdir(dirindex)
    if len(os.listdir(dirindex)) == 0:
        check = False
    return check


def add_doc(writer, ean, descripcionMM, descripcionECI):
    writer.add_document(ean=ean, descripcionMM=descripcionMM, descripcionECI=descripcionECI)
