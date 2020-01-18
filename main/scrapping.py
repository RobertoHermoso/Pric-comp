from bs4 import BeautifulSoup
import urllib.request, re
import re


def open_url(url, file):
    f = urllib.request.urlretrieve(url, file)
    return file


def extract_data_elCorteIngles(key_word):
    res = []
    fichero = "elCorteIngles"
    key_word = key_word.replace(" ", "+")
    url = "https://www.elcorteingles.es/search?s=" + key_word
    if open_url(url, fichero):
        f = open(fichero, encoding="utf-8")
        s = f.read()
        soup = BeautifulSoup(s, "html.parser")
        products = soup.findAll("div", "product-preview")
        for product in products:
            aLabels = product.findAll("a", "event")
            url = ""
            for a in aLabels:
                if a['href']:
                    i = 0

        return res


def extract_data_mediaMarkt(key_word):
    res = []
    fichero = "mediaMarkt"
    key_word = key_word.replace(" ", "+")
    url = "https://www.mediamarkt.es/es/search.html?query=" + key_word + "&searchProfile=onlineshop&channel=mmeses"
    if open_url(url, fichero):
        f = open(fichero, encoding="utf-8")
        s = f.read()
        soup = BeautifulSoup(s, "html.parser");

        products = soup.find("ul", class_="products-list")
        if products is not None:
            products = products.findAll('div', class_='product-wrapper');
            for product in products:
                name = product.find("h2").find("a").contents[0]
                regex = re.compile(r'[\n\r\t]')
                name = regex.sub("", name)
                res.append(name)
        else:
            name = soup.find("h1", itemprop="name").contents[0]
            res.append(name)
        return res