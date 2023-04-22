import os
import requests
import csv
from bs4 import BeautifulSoup

URL = "https://www.marca.com/"

# Se cambia el User-Agent para evitar que nos deneguen el permiso
headers = {
    'User-Agent': 'Mozilla/5.0'
}

response = requests.post(URL, headers=headers)
soup = BeautifulSoup(response.text,"html.parser")

links = []
for link in soup.find_all('a'):
    links.append(link.get('href'))

links_clasificaciones = []
for link in links:
    if(link.find("clasificacion") != -1):
        links_clasificaciones.append(link)
        print(link)

print("\n\n------------------------------------------------------\n\n")

links_resultados = []
for link in links:
    if(link.find("resultados") != -1 and link.find("clasificacion") == -1):
        links_resultados.append(link)
        print(link)