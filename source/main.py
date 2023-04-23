from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import time

# En primer lugar, cambiamos los headers para evitar ser identificados como script y no nos bloqueen.
headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\*/*;q=0.8", 
           "Accept-Encoding": "gzip, deflate, sdch, br",
           "Accept-Language": "en-US,en;q=0.8",
           "Cache-Control": "no-cache",
           "dnt": "1",
           "Pragma": "no-cache",
           "Upgrade-Insecure-Requests": "1",
           "User-Agent": "Mozilla/5.0"
          }
sitio_web = "https://preciosmundi.com"
sitio_web_xml = "https://preciosmundi.com/sitemap.xml"

def extraer_soup(website, header):
# Extraemos directamente la información en formato xml del sitemap. 
# Cargamos la información del sitio usando BeautifulSoup:
    web = requests.get(website,headers=header) # Obtenemos la información del sitemap
    return BeautifulSoup(web.text,'xml') # Creamos un objeto soup para facilitar la navegación del xml
    
soup = extraer_soup(sitio_web_xml, headers)

# Vemos que las páginas web van entre dos etiquetas <loc> </loc> y dos etiquetas <url> </url>:

urls = soup.find_all("loc") # Buscamos todos los loc
print(urls)

# Ahora obtenemos el texto que está entre las dos etiquetas (las diferentes URL) y lo guardamos en una lista.
url_list=[]
for a in urls:
    url_list.append(a.get_text())

# Nos paramos a observar los 20 primeros elementos de la lista de url's para ver cuáles debemos descartar.
print(url_list[1:21])

# Los 17 primeros elementos de la listan no nos interesan para este trabajo en particular, dado que solo queremos obtener tablas de precios en los distintos países. Por tanto, los eliminamos.
del url_list[0:18]

print(url_list[1:21])
# Podemos ver que cada país tiene 7 páginas web diferentes donde está almacenada la información. El objetivo de ese trabajo es extraer los datos de precios de ropa y calzado para todos los países que aparecen en esta página web.
len(url_list) 

# Existen 980 elementos en la lista, divididos en 140 grupos de 7 elementos cada uno (País+super+restaurante+ropa+calzado+transporte+vivienda+ocio). 
# Por lo tanto, hay 140 países diferentes. Seleccionamos sólo las url de precios de ropa y calzado, aprovechando que están estructurados de manera periódica.
# Como todos los países tienen las mismas páginas y hay 140 países, podemos coger la tercera página de cada grupo de 7.
url_subList = [url_list[n+3] for n in range(0, len(url_list), 7)] 
url_subList
print(url_subList)

def dinero_ropa_pais(url,header):
    web = requests.get(url,headers=header) # Obtenemos la página web
    soup_real = BeautifulSoup(web.text,'html') # Tranformamos en objeto soup
    data_url = soup_real.find('div',{'class':'table-responsive-md'}) #Buscamos la tabla, esto lo hicimos con ayuda de un navegador
    
    country=url.replace('/', ' ').split()[2].capitalize() #Cogemos el país de la url y le ponemos la primera letra mayúscula
    columns=['Unos zapatos de hombre de cuero',
       'Unas zapatillas deportivas de marca (Nike, Adidas, Puma, etc.)',
       'Un vestido (Zara, H&M, etc.)',
       'Unos vaqueros Levis 501 (o equivalente)'] #Nombres de las columnas de precios de vivienda
    
    if data_url != None: #En el caso de que la página web tenga una tabla hacemos esto
        real_state_table= str(data_url)
        df_temp = pd.read_html(real_state_table)
        df_temp = df_temp[0]
        df_temp['DÃ³lar ($)'] = df_temp['DÃ³lar ($)'].str.replace('$', '') #Cambios de estilo en el dataframe
        df_temp['DÃ³lar ($)'] = df_temp['DÃ³lar ($)'].str.replace(',', '.')
        df_temp['DÃ³lar ($)'] = df_temp['DÃ³lar ($)'].astype(float)
        selected_columns = df_temp[['Producto','DÃ³lar ($)']] #Mantenemos sólo el precio en dólares
        df_temp2 = selected_columns.copy()
        df_temp2.columns = ['Producto','Precio en dólares'] #Cambiamos el nombre para que quede más presentable
        df_temp3=df_temp2.transpose() #Queremos cada país como una fila, y esta al revés. Transponemos
        df_temp3.columns=list(df_temp3.iloc[0]) #Al trasponer el nombre de las columnas es una fila del dataframe
        df_temp3=df_temp3.drop(df_temp3.index[0]) #Lo solucionamos y guardamos el nombre
        df_temp4 = df_temp3.rename(index={'Precio en dólares':country}) #Renombramos la fila al nombre del país
        time.sleep(0.5) #Para evitar hacer muchas peticiones al sitio, obligamos a parar 0.5 segundos después de cada petición.
        return(df_temp4)
    
    else: #Si no tiene tabla creamos un dataframe con nans para retornarlo
        print('Sin información de precios de ropa y calzado en '+ country)
        df_null=pd.DataFrame(np.zeros([1, 4])*np.nan).rename(index={0:country})
        df_null.columns=columns
        return(df_null)
    

df = pd.DataFrame() 
for url in url_subList:
    df_temp=dinero_ropa_pais(url,headers)
    df=pd.concat([df,df_temp])
    
df.columns=['Unos zapatos de hombre de cuero (USD)',
       'Unas zapatillas deportivas de marca (Nike, Adidas, Puma, etc.) (USD)',
       'Un vestido (Zara, H&M, etc.) (USD)',
       'Unos vaqueros Levis 501 (o equivalente) (USD)']

print(df)
df.to_csv('PreciosRopaPorPais.csv')
