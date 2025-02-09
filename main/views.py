from django.shortcuts import render
from .forms import *
from .scrapping import *
from .models import *
import datetime
import os
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, NUMERIC
from whoosh.query import Or, And, Term

dirindex = "main/index"
dirhtml = "main/html"

# Index
def index(request):
    return render(request, "index.html", {"title": "¡Bienvenido!"})


# Search engine
def search(request):
    if request.method == 'POST':
        form = Search_Form(request.POST)
        if form.is_valid():
            if not aux_check_index():
                aux_reset_all()
            key = form.cleaned_data['key_word'].lower()
            type = form.cleaned_data['type']
            ix = open_dir(dirindex)
            with ix.searcher() as searcher:
                words = key.strip().split()
                terms_classified = []
                for word in words:
                    terms = []
                    for desc in ['descripcionECI', 'descripcionMM', 'descripcionFC']:
                        terms.append(Term(desc, word))
                    terms_classified.append(terms)
                subqueries = []
                for t in terms_classified:
                    if type == 'N3':
                        subqueries.append(And(t))
                    else:
                        subqueries.append(Or(t))
                query = subqueries[0]
                if len(subqueries) > 1:
                    if type == 'N1':
                        query = Or(subqueries)
                    else:
                        query = And(subqueries)
                results = searcher.search(query)
                title = "Resultados para: "
                mostrar = True
                if len(results) == 0:
                    title = "No hay resultados para: "
                    mostrar = False
                eci = []
                mm = []
                fc = []
                for r in results:
                    eci.append(Historico_ECI.objects.filter(producto_id=r['ean']).order_by("-fecha")[0])
                    mm.append(Historico_MM.objects.filter(producto_id=r['ean']).order_by("-fecha")[0])
                    fc.append(Historico_FC.objects.filter(producto_id=r['ean']).order_by("-fecha")[0])
                return render(request, 'search.html', {"eci": eci, "mm": mm, 'fc': fc, "title": title + key, "mostrar": mostrar})
    else:
        form = Search_Form()
    return render(request, 'search.html', {'form': form})


def compare(request):
    if request.method == 'GET':
        form = Compare_Form()
        return index(request)
    else:
        form = Compare_Form(request.POST)
        if form.is_valid():
            aux_check_create_html()
            if not aux_check_index():
                aux_reset_all()
            key = form.cleaned_data['key_word']
            pagination = form.cleaned_data['pagination']
            iterable = False
            if pagination == 'S':
                iterable = True
            eci = extract_data_elCorteIngles(key, iterable)
            mm = extract_data_mediaMarkt(key, iterable)
            fn = extract_data_fnac(key, iterable)
            eci_ean = set()
            mm_ean = set()
            fn_ean = set()
            fecha = datetime.datetime.now()
            for prod in eci:
                num_results = Producto_ECI.objects.filter(ean = str(prod["ean"])).count()
                if num_results == 0:
                    Producto_ECI.objects.create(ean=str(prod["ean"]), nombre=str(prod["title"]), descripcion=str(prod["description"]), link=str(prod["link"]), image=str(prod['image']))
                else:
                    Producto_ECI.objects.filter(ean = str(prod["ean"])).update(nombre=str(prod["title"]), descripcion=str(prod["description"]), link=str(prod["link"]), image=str(prod['image']))
                historico = Historico_ECI.objects.filter(producto_id=prod["ean"]).order_by("-fecha")

                #We check if is not void
                if len(historico)>0:
                    #We check if the price changed
                    if historico[0].precio!= prod["price"]:
                        Historico_ECI.objects.create(fecha=fecha, producto_id=str(prod["ean"]), precio=str(prod["price"]))
                else:
                    Historico_ECI.objects.create(fecha=fecha, producto_id=str(prod["ean"]), precio=str(prod["price"]))
                eci_ean.add(str(prod["ean"]))
            for prodM in mm:
                num_results = Producto_MM.objects.filter(ean = str(prodM["ean"])).count()
                if num_results == 0:
                    Producto_MM.objects.create(ean=str(prodM["ean"]), nombre=str(prodM["title"]), descripcion=str(prodM["description"]), link=str(prodM["link"]), image=str(prodM['image']))
                else:
                    Producto_MM.objects.filter(ean = str(prodM["ean"])).update(nombre=str(prodM["title"]), descripcion=str(prodM["description"]), link=str(prodM["link"]), image=str(prodM['image']))
                historico = Historico_MM.objects.filter(producto_id=prodM["ean"]).order_by("-fecha")
                #We check if is not void
                if len(historico)>0:
                    #We check if the price changed
                    if historico[0].precio!= prodM["price"]:
                        Historico_MM.objects.create(fecha=fecha, producto_id=str(prodM["ean"]), precio=str(prodM["price"]))
                else:
                    Historico_MM.objects.create(fecha=fecha, producto_id=str(prodM["ean"]), precio=str(prodM["price"]))
                mm_ean.add(str(prodM["ean"]))
                
            for prodF in fn:
                num_results = Producto_FC.objects.filter(ean = str(prodF["ean"])).count()
                if num_results == 0:
                    Producto_FC.objects.create(ean=str(prodF["ean"]), nombre=str(prodF["title"]), descripcion=str(prodF["description"]), link=str(prodF["link"]), image=str(prodF['image']))
                else:
                    Producto_FC.objects.filter(ean = str(prodF["ean"])).update(nombre=str(prodF["title"]), descripcion=str(prodF["description"]), link=str(prodF["link"]), image=str(prodF['image']))
                historico = Historico_FC.objects.filter(producto_id=prodF["ean"]).order_by("-fecha")
                #We check if is not void
                if len(historico)>0:
                    #We check if the price changed
                    if historico[0].precio!= prodF["price"]:
                        Historico_FC.objects.create(fecha=fecha, producto_id=str(prodF["ean"]), precio=str(prodF["price"]))
                else:
                    Historico_FC.objects.create(fecha=fecha, producto_id=str(prodF["ean"]), precio=str(prodF["price"]))
                fn_ean.add(str(prodF["ean"]))
            l = list(eci_ean & mm_ean & fn_ean)
            mostrar = False
            title = "No hay resultados comunes para: "
            prod_eci = []
            prod_mm = []
            prod_fc = []
            if len(l) > 0:
                ix = open_dir(dirindex)
                writer = ix.writer()
                mostrar = True
                title = "Resultados para: "
                for e in l:
                    eci = Historico_ECI.objects.filter(producto_id=e).order_by("-fecha")[0]
                    mm = Historico_MM.objects.filter(producto_id=e).order_by("-fecha")[0]
                    fc = Historico_FC.objects.filter(producto_id=e).order_by("-fecha")[0]
                    ix = open_dir(dirindex)
                    with ix.searcher() as searcher:
                        query = Term('ean', e)
                        if len(searcher.search(query))>0:
                            delete_doc(writer, searcher, e)
                    add_doc(writer, e, mm.producto.descripcion.strip(), eci.producto.descripcion.strip(), fc.producto.descripcion.strip())
                    prod_eci.append(eci)
                    prod_mm.append(mm)
                    prod_fc.append(fc)
                writer.commit()
            return render(request, 'results.html', {"eci": prod_eci, "mm": prod_mm, 'fc': prod_fc, "title": title + key, "mostrar": mostrar})
        return index(request)


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
    elif web =='fc':
        res = Historico_FC.objects.filter(producto_id=key).order_by("-fecha")
        shop = "Fnac"
        color = "#CCCC00"
    return render(request, 'historial_price.html', {"res": res,"name": name, 'shop':shop, 'color':color})

def reset_all(request):
    aux_reset_all()
    return render(request, 'message.html', {"message": "Base de datos reseteada"})


def list_all(request):
    eci = []
    mm = []
    fc = []
    ean_eci = set()
    ean_mm = set()
    ean_fc = set()
    for p in Producto_ECI.objects.all():
        ean_eci.add(p.ean)
    for p in Producto_MM.objects.all():
        ean_mm.add(p.ean)
    for p in Producto_FC.objects.all():
        ean_fc.add(p.ean)
    ean = list(ean_eci & ean_mm & ean_fc)
    for e in ean:
        eci.append(Historico_ECI.objects.filter(producto_id=e).order_by("-fecha")[0])
        mm.append(Historico_MM.objects.filter(producto_id=e).order_by("-fecha")[0])
        fc.append(Historico_FC.objects.filter(producto_id=e).order_by("-fecha")[0])
    return render(request, 'results.html', {"eci": eci, "mm": mm, 'fc': fc, "title": "Estos son todos los resultados", "mostrar": True})

# Métodos auxiliares

def aux_reset_all():
    aux_reset_bd()
    aux_reset_index()

def aux_reset_index():
    if not os.path.exists(dirindex):
        os.mkdir(dirindex)
    ix = create_in(dirindex, schema=Schema(ean=NUMERIC(int, 64, stored=True), descripcionMM=TEXT(stored=True), descripcionECI=TEXT(stored=True), descripcionFC=TEXT(stored=True)))
    writer = ix.writer()
    writer.commit()


def aux_reset_bd():
    Producto_ECI.objects.all().delete()
    Producto_MM.objects.all().delete()
    Historico_ECI.objects.all().delete()
    Historico_MM.objects.all().delete()
    Historico_FC.objects.all().delete()
    Producto_FC.objects.all().delete()


def aux_check_index():
    check = True
    if not os.path.exists(dirindex):
        os.mkdir(dirindex)
    if len(os.listdir(dirindex)) == 0:
        check = False
    return check


def aux_check_create_html():
    if not os.path.exists(dirhtml):
        os.mkdir(dirhtml)


def add_doc(writer, ean, descripcionMM, descripcionECI, descripcionFC):
    writer.add_document(ean=ean, descripcionMM=descripcionMM, descripcionECI=descripcionECI, descripcionFC=descripcionFC)

def delete_doc(writer, searcher, ean):
    writer.delete_by_term("ean", ean, searcher)