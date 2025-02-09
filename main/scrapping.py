from bs4 import BeautifulSoup
import urllib.request, urllib.parse
import re
import json as jsonConverter
from .models import *

product_set = set()

def open_url(url, file):
    urllib.request.urlretrieve(url, file)
    return file

#------------------------------------ Srapping EL CORTE INGLES ---------------------------------------

def extract_data_elCorteIngles(key_word, iterable):
    res = []
    fichero = "main/html/elCorteIngles"
    fichero2 = "main/html/elCorteInglesElement"
    key_word = urllib.parse.quote(key_word)
    page = 1
    numPags = 0
    continua = True
    while continua:
        url = "https://www.elcorteingles.es/search/" + str(page) + "/?s=" + key_word
        if open_url(url, fichero):
            f = open(fichero, encoding="utf-8")
            s = f.read()
            soup = BeautifulSoup(s, "html.parser")
            if page == 1:
                try:
                    numPags = int(str(soup.find("div", "pagination").find("div", "mobile-view").contents[0]).split("de")[1])
                except:
                    continua = False
            if continua:
                page = page + 1
                if page > numPags or not iterable:
                    continua = False
            products = soup.findAll("div", "product-preview")
            for product in products:
                try:
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
                        image = 'https:' + soup2.find('img', id='product-image-placer').get('src')
                        price = ""
                        for span in spanLabels:
                            if span["itemprop"] == "price":
                                price = span.contents[0]
                                break
                        description = ""
                        try:
                            descs = soup2.find("div", "description-container").findAll("p", "content")
                            for desc in descs:
                                description = description + desc.contents[0]
                        except:
                            pass
                        try:
                            references = soup2.find("div", "reference").findAll("span")
                            ean = ""
                            for ref in references:
                                if "id" in ref.attrs:
                                    if ref["id"] == "ean-ref":
                                        ean = ref.contents[0]
                                        res.append(
                                            {"ean": ean, "title": title, "description": description, "price": price,
                                             "link": link, 'image': image})
                                        break
                        except:
                            pass
                except:
                    continue
    return res

#------------------------------------ Srapping MEDIA MARKT ---------------------------------------
def extract_data_mediaMarkt(key_word, iterable):
    res = []
    product_set.clear() 
    fichero = "main/html/mediaMarkt"
    ficheroElement = "main/html/mediaMarktElement"
    aux = True
    currentPage = 1
    key_word = urllib.parse.quote(key_word)
    url = "https://www.mediamarkt.es/es/search.html?query=" + key_word + "&searchProfile=onlineshop&channel=mmeses"
    while aux:
        if open_url(url, fichero):
            f = open(fichero, encoding="utf-8")
            s = f.read()
            soup = BeautifulSoup(s, "html.parser")
            if currentPage == 1:
                pages = soup.find('ul', class_="pagination")
                if pages is not None:
                    pages = pages.findAll('li')
                    pages = pages[len(pages)-2].get('data-value')
                else:
                    pages = 1

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
                        res = extract_an_element_MM(res, soup, link)
            #One element        
            else:
                res = extract_an_element_MM(res, soup, url)
        if int(currentPage) == int(pages) or not iterable:
            break
        else:
            currentPage+=1
            url = "https://www.mediamarkt.es/es/search.html?query=" + key_word + "&searchProfile=onlineshop&channel=mmeses&page="+ str(currentPage)
            print(url)
    return res

def extract_an_element_MM(res, soup, link):
    try:
        scripts = soup.findAll("script")
        jsonProduct = {}
        for script in scripts:
            if len(script.contents)>0:
                vars = script.contents[0].split(';')
                for var in vars:
                    if len(var.split("="))==2:
                        try:
                            jsonVar = jsonConverter.loads(var.split("=")[1].strip())
                            if 'ean' in jsonVar:
                                jsonProduct = jsonVar
                                break
                        except:
                            continue
                if 'ean' in jsonProduct:
                    ean = jsonProduct['ean']
                    nombre = jsonProduct['name']
                    price = jsonProduct ['price']
                    ps =  soup.find("article", class_="description")
                    description = ps.get_text()
                    description = description.replace('Descripción', '')
        image = 'https:' + soup.find('div', class_="preview").find('a').get('href')
        if ean not in product_set:

            attributes = {'ean' : ean,'title':nombre, 'price':price, 'link': link, 'description':description, 'image': image}
            product_set.add(ean)
            res.append(attributes)
    except:
        pass
    return res

#------------------------------------ Srapping FNAC ---------------------------------------

def extract_data_fnac(key_word, iterable):
    res = []
    fichero = "main/html/fnac"
    ficheroElement = "main/html/fnacElement"
    key_word = urllib.parse.quote(key_word)
    aux = True
    currentPage = 1

    url = "https://www.fnac.es/SearchResult/ResultList.aspx?SCat=0%211&Search=" + key_word + "&sft=1&sa=0"
    while aux:
        print(aux)
        if open_url(url, fichero):
            f = open(fichero, encoding="utf-8")
            s = f.read()
            soup = BeautifulSoup(s, "html.parser")

            #Pages
            if (currentPage==1):
                pages = soup.find('li', class_="pageView").get_text().split('/')[1].strip()
            products = soup.findAll("article", class_="Article-itemGroup js-article-thumbnail")

            for product in products:
                link = product.find("a").get('href')
                if open_url(link, ficheroElement):
                    try:
                        f1 = open(ficheroElement, encoding='utf-8')
                        s1 = f1.read()
                        soup = BeautifulSoup(s1, "html.parser")
                        #EAN
                        ean = soup.find('div', class_="f-productHeader-additionalInformation f-productHeader-review").find('span').get('data-ean')
                        #Title
                        title = soup.find('h1', class_="f-productHeader-Title").get_text().strip()
                        #Description
                        if soup.find('div', class_="whiteContent js-productSummaryTrimHeight-target"):
                            description = soup.find('div', class_="whiteContent js-productSummaryTrimHeight-target").get_text()
                        else:
                            description = 'No hay descprición'
                        #Price
                        prices =  soup.find('div', class_="f-priceBox").findAll("span")
                        if len(prices)==2:
                            price = prices[1].get_text().replace('€','')
                        else:
                            price = soup.find('div', class_="f-priceBox").get_text().replace("€", "")
                        #Image
                        image = soup.find('img', class_="f-productVisuals-mainMedia js-ProductVisuals-imagePreview").get('src')
                        attributes = {'ean' : ean,'title':title, 'price':price, 'link': link, 'description':description, 'image':image}
                        res.append(attributes)
                    except:
                        continue
        if int(currentPage) == int(pages) or not iterable:
            break
        else:
            currentPage+=1
            print(currentPage)
            print(pages)
            url="https://www.fnac.es/SearchResult/ResultList.aspx?PageIndex=" + str(currentPage) + "&Search="+ key_word+ "&sft=1&sl"
            print(url)
    return res

