import os
import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata


URL = "https://resultados.as.com/resultados/"

# Se cambia el User-Agent para evitar que nos deneguen el permiso
headers = {
    'User-Agent': 'Mozilla/5.0'
}


def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').title().strip()

def obtenerPartidos(soup):
    resultados = []

    # Se obtiene el nombre de la competicion
    nombre_competicion = normalize(soup.find('div', {'class': 'txt-competicion'}).find("a").text)

    # Se obtienen los partidos
    partidos = soup.find_all('li', {'class': 'list-resultado'})
    for partido in partidos:
        # Se obtienen los equipos y goles locales y visitantes
        equipo_local = partido.find('div', {'class': 'equipo-local'}).find('span', {'class': 'nombre-equipo'}).text
        equipo_visitante = partido.find('div', {'class': 'equipo-visitante'}).find('span', {'class': 'nombre-equipo'}).text
        
        resultado = partido.find('a', {'class': 'resultado'})
        if(resultado == None):
            resultado = partido.find('span', {'class': 'resultado'})
        resultado = resultado.text.replace(" ", "").replace("\n", "")
        puntos_local = resultado.split("-")[0]
        puntos_visitante = resultado.split("-")[1]

        # Se normaliza el nombre de los equipos
        """
        Correcciones:
        * Almería 0-1 Athletic Club -> Almeria 0-1 Athletic Club
        * OSASUNA 3-2 BETIS -> Osasuna 3-2 Betis
        * Hawks 130-122 Celtics (1-2) -> Hawks 130-122 Celtics
        """
        equipo_local = normalize(equipo_local)
        equipo_visitante = normalize(equipo_visitante)

        resultados.append({
            "nombre_competicion": nombre_competicion, 
            "fecha": fecha, 
            "equipo_local": equipo_local, 
            "equipo_visitante": equipo_visitante, 
            "puntos_local": puntos_local, 
            "puntos_visitante": puntos_visitante
        })

    return resultados

def obtenerPartidosFutbol(soup):
    resultados = []
    # Se obtienen las competiciones
    competiciones = soup.find_all('div', {'class': 'cont-modulo resultados', "id": lambda x: x and "futbol" in x})
    for competicion in competiciones:
        resultados += obtenerPartidos(competicion)

    return resultados

def obtenerPartidosBaloncesto(soup):
    resultados = []
    # Se obtienen las competiciones
    competiciones = soup.find_all('div', {'class': 'cont-modulo resultados', "id": lambda x: x and "baloncesto" in x})
    for competicion in competiciones:
        resultados += obtenerPartidos(competicion)

    return resultados

def obtenerPartidosTenis(soup):
    resultados = []
    # Se obtienen las competiciones
    competiciones = soup.find_all('div', {'class': 'cont-modulo resultados', "id": lambda x: x and "tenis" in x})
    for competicion in competiciones:
        resultados += obtenerPartidos(competicion)

    return resultados

fecha = datetime.now().strftime('%Y/%m/%d/')
URL_aux = URL + fecha

response = requests.post(URL_aux, headers=headers)
soup = BeautifulSoup(response.text,"html.parser")

# arrow = soup.find('a', {'class': 'slick-prev slick-arrow'})
# href = arrow.get('href')
# date = href.split("/resultados/")[1]
# print(date)

deportes = soup.find_all('h2', {'class': 'tit-decoration2'})
deportes_explorados = set()
for deporte in deportes:
    nombre_deporte = normalize(deporte.text)

    # En algunas ocasiones aparece dos veces el mismo deporte en dos secciones distintas
    if (nombre_deporte not in deportes_explorados):
        if (nombre_deporte == "Futbol"):
            partidos = obtenerPartidosFutbol(soup)
            deportes_explorados.add(nombre_deporte)
            # Se escriben las cabeceras del fichero CSV
            with open('../dataset/partidos_futbol.csv', mode='w', newline='', encoding='utf-8') as fichero_partidos:
                fichero_partidos = csv.writer(fichero_partidos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                fichero_partidos.writerow([
                    'Competicion', 
                    'Fecha', 
                    'Equipo local', 
                    'Equipo visitante', 
                    'Goles local', 
                    'Goles visitante'
                ])
                # Se escriben los datos del partido en el fichero CSV
                for partido in partidos:
                    # fichero_partidos = csv.writer(fichero_partidos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    fichero_partidos.writerow([
                        partido["nombre_competicion"], 
                        partido["fecha"], 
                        partido["equipo_local"], 
                        partido["equipo_visitante"], 
                        partido["puntos_local"], 
                        partido["puntos_visitante"]
                    ])

        elif (nombre_deporte == "Baloncesto"):
            partidos = obtenerPartidosBaloncesto(soup)
            deportes_explorados.add(nombre_deporte)
            
            # Se escriben las cabeceras del fichero CSV
            with open('../dataset/partidos_baloncesto.csv', mode='w', newline='', encoding='utf-8') as fichero_partidos:
                fichero_partidos = csv.writer(fichero_partidos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                fichero_partidos.writerow([
                    'Competicion', 
                    'Fecha', 
                    'Equipo local', 
                    'Equipo visitante', 
                    'Puntos local', 
                    'Puntos visitante'
                ])
                # Se escriben los datos del partido en el fichero CSV
                for partido in partidos:
                    # fichero_partidos = csv.writer(fichero_partidos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    fichero_partidos.writerow([
                        partido["nombre_competicion"], 
                        partido["fecha"], 
                        partido["equipo_local"], 
                        partido["equipo_visitante"], 
                        partido["puntos_local"], 
                        partido["puntos_visitante"]
                    ])

        else:
            print(nombre_deporte + " sin implementar !!!")
    