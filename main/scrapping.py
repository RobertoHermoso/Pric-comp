from bs4 import BeautifulSoup
import urllib.request, re
import re
import json
from .models import *


def open_url(url, file):
    urllib.request.urlretrieve(url, file)
    return file


def extract_data_elCorteIngles(key_word):
    res = []
    fichero = "elCorteIngles"
    fichero2 = "elCorteIngles2"
    key_word = key_word.replace(" ", "+")
    url = "https://www.elcorteingles.es/search?s=" + key_word
    if open_url(url, fichero):
        f = open(fichero, encoding="utf-8")
        s = f.read()
        soup = BeautifulSoup(s, "html.parser")
        products = soup.findAll("div", "product-preview")
        for product in products:
            aLabels = product.findAll("a", "event")
            link = "https://www.elcorteingles.es"
            for a in aLabels:
                if a["data-event"] == "product_click":
                    link = link + a["href"]
                    break
            if open_url(link, fichero2):
                fp = open(fichero2, encoding="utf-8")
                sp = fp.read()
                soup2 = BeautifulSoup(sp, "html.parser")
                title = soup2.find("h2", "title").contents[0]
                spanLabels = soup2.find("div", "product-price").findAll("span", "hidden")
                price = ""
                for span in spanLabels:
                    if span["itemprop"] == "price":
                        price = span.contents[0]
                        break
                description = ""
                descs = soup2.find("div", "description-container").findAll("p", "content")
                for desc in descs:
                    description = description + desc.contents[0]
                references = soup2.find("div", "reference").findAll("span")
                ean = ""
                for ref in references:
                    if "id" in ref.attrs:
                        if ref["id"] == "ean-ref":
                            ean = ref.contents[0]
                            res.append({"ean": ean, "title": title, "description": description, "price": price, "link": link})
                            break
        return res


def extract_data_mediaMarkt(key_word):
    res = {}
    fichero = "mediaMarkt"
    ficheroElement = "mediaMarktElement"
    key_word = key_word.replace(" ", "+")
    url = "https://www.mediamarkt.es/es/search.html?query=" + key_word + "&searchProfile=onlineshop&channel=mmeses"
    if open_url(url, fichero):
        f = open(fichero, encoding="utf-8")
        s = f.read()
        soup = BeautifulSoup(s, "html.parser")

        products = soup.find("ul", class_="products-list")
        #List
        if products is not None:
            products = products.findAll('div', class_='product-wrapper')
            for product in products:
                link ="https://www.mediamarkt.es"+ product.find("h2").find("a").get('href')
                if open_url(link, ficheroElement):
                    f1 = open(ficheroElement, encoding='utf-8')
                    s1 = f1.read()
                    soup = BeautifulSoup(s1, "html.parser")
                    res = extract_an_element_MM(res, soup)
        #One element        
        else:
            res = extract_an_element_MM(res, soup)
        return res
    
def extract_an_element_MM(res, soup):
    scripts = soup.findAll("script")
    jsonProduct = json.loads(scripts[16].contents[0].split(';')[0].split("=")[1])
    if 'ean' in jsonProduct:
        ean = jsonProduct['ean']
        nombre = jsonProduct['name']
        price = jsonProduct ['price']
        attributes = [nombre, price]
        res[ean]= attributes
        
    return res
    
print(extract_data_mediaMarkt("Persona 5"))