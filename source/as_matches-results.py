import requests
import pandas as pd
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

# Buscamos que no haya error 404 por sitio web obsoleto o eliminado
def resultadosDisponibles(soup):
    return soup.find('span', string='404') == None

def obtenerPartidos(soup, fecha):
    resultados = pd.DataFrame(columns=['Competicion','Jornada','Fecha','Equipo local','Equipo visitante','Puntos local','Puntos visitante'])

    # Se obtiene el nombre de la competicion
    nombre_competicion = normalize(soup.find('div', {'class': 'txt-competicion'}).find("a").text)
    jornada = soup.find('div', {'class': 'txt-jornada'}).find('span').text

    # Se obtienen los partidos
    partidos = soup.find_all('li', {'class': 'list-resultado'})
    for partido in partidos:
        # Se obtienen los equipos y puntos/goles locales y visitantes
        equipo_local = partido.find('div', {'class': 'equipo-local'}).find('span', {'class': 'nombre-equipo'}).text
        equipo_visitante = partido.find('div', {'class': 'equipo-visitante'}).find('span', {'class': 'nombre-equipo'}).text

        resultado = partido.find('a', {'class': 'resultado'})
        if(resultado == None):
            resultado = partido.find('span', {'class': 'resultado'})
        resultado = resultado.text.replace(" ", "").replace("\n", "")

        try:
            puntos_local = resultado.split("-")[0]
        except:
            puntos_local = None
        try:
            puntos_visitante = resultado.split("-")[1]
        except:
            puntos_visitante = None

        # Se normaliza el nombre de los equipos
        """
        Correcciones:
        * Almería 0-1 Athletic Club -> Almeria 0-1 Athletic Club
        * OSASUNA 3-2 BETIS -> Osasuna 3-2 Betis
        * Hawks 130-122 Celtics (1-2) -> Hawks 130-122 Celtics
        """
        equipo_local = normalize(equipo_local)
        equipo_visitante = normalize(equipo_visitante)

        resultados = resultados._append({
            'Competicion':nombre_competicion,
            'Jornada':jornada,
            'Fecha':fecha,
            'Equipo local':equipo_local,
            'Equipo visitante':equipo_visitante,
            'Puntos local':puntos_local,
            'Puntos visitante':puntos_visitante
        }, ignore_index=True)

    return resultados

def obtenerPartidosFutbol(soup, fecha):
    resultados = pd.DataFrame()
    # Se obtienen las competiciones de futbol
    competiciones = soup.find_all('div', {'class': 'cont-modulo resultados', "id": lambda x: x and "futbol" in x})
    for competicion in competiciones:
        resultados = pd.concat([resultados,obtenerPartidos(competicion, fecha)])

    return resultados

def obtenerPartidosBaloncesto(soup, fecha):
    resultados = pd.DataFrame()
    # Se obtienen las competiciones de baloncesto
    competiciones = soup.find_all('div', {'class': 'cont-modulo resultados', "id": lambda x: x and "baloncesto" in x})
    for competicion in competiciones:
        resultados = pd.concat([resultados,obtenerPartidos(competicion, fecha)])

    return resultados

fecha = datetime.now().strftime('%Y/%m/%d/')
URL_aux = URL + fecha

response = requests.post(URL_aux, headers=headers)
soup = BeautifulSoup(response.text,"html.parser")

df_futbol = pd.DataFrame()
df_baloncesto = pd.DataFrame()

while(resultadosDisponibles(soup)):
    fecha = fecha[:-1] # Se elimina el carácter '/' del final
    print("Obteniendo datos de {0}...".format(fecha))

    deportes = soup.find_all('h2', {'class': 'tit-decoration2'})
    deportes_explorados = set()
    for deporte in deportes:
        nombre_deporte = normalize(deporte.text)

        # En algunas ocasiones aparece dos veces el mismo deporte en dos secciones distintas
        if (nombre_deporte not in deportes_explorados):
            if (nombre_deporte == "Futbol"):
                df_futbol = pd.concat([df_futbol,obtenerPartidosFutbol(soup, fecha)])
                deportes_explorados.add(nombre_deporte)

            elif (nombre_deporte == "Baloncesto"):
                df_baloncesto = pd.concat([df_baloncesto,obtenerPartidosFutbol(soup, fecha)])
                deportes_explorados.add(nombre_deporte)

    # Obtengo la URL del dia anterior
    dia_previo = soup.find('a', {'class': 'slick-prev slick-arrow'})
    fecha = dia_previo.get('href').split("/resultados/")[1]
    URL_aux = URL + fecha
    response = requests.post(URL_aux, headers=headers)
    soup = BeautifulSoup(response.text,"html.parser")



# Se guardan los datos en un CSV
df_futbol.columns=['Competicion','Jornada','Fecha','Equipo local','Equipo visitante','Goles local','Goles visitante']
df_futbol.to_csv('../dataset/partidos_futbol.csv', index=False)

df_baloncesto.columns=['Competicion','Jornada','Fecha','Equipo local','Equipo visitante','Puntos local','Puntos visitante']
df_baloncesto.to_csv('../dataset/partidos_baloncesto.csv', index=False)

print("------------------------------------")
print("FIN DEL PROCESO")
print("------------------------------------")
    