import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import numpy as np
import folium

def data_reading():

    df = pd.read_excel("UsuarioSoftwareGriluLabsica.xls", sep=';')
    df = df.rename(columns = {"Pessoa Fisica": "Tipo de Usuário", 
                          "1.1": "Quantidade de Registros",
                          "Provisório":"Nome da Instituição",
                          "Provisório.1":"Sigla da Instituição", 
                          "Outra":"Tipo de Instituição", 
                          "Unnamed: 6":"Endereço da Instituição/Empresa",  
                          "Unnamed: 7":"CEP da Instituição/Empresa", 
                          "Provisório.2":"Cidade", 
                          "Exterior":"Estado", 
                          "Provisório.3":"País",   
                          "Provisório.4":"Nome",  
                          "Outra.1":"Formação (Graduação)",
                          "Unnamed: 14":"CPF", 
                          "Unnamed: 15":"Endereço do Usuário",
                          "Unnamed: 11":"CEP",
                          "Unnamed: 17":"Telefone",
                          "Graduação":"Titulação",
                          "Em Andamento":"Situação da Titulação",
                          "grilu@hotmail.com":"Email", 
                          "30/08/19": "Data do Registro",
                          "Unnamed: 22": "Hora do Registro"})
    return df

#_________________________________________________________________________________________________________________________________
#Avoiding GeocoderTimedOut

def do_geocode(address):
    #geopy = Nominatim(timeout=3)
    geopy = Nominatim(user_agent="mapa-localizacao-dos-usuarios")
    try:
        return geopy.geocode(address,exactly_one=True)
    except GeocoderTimedOut:
        return do_geocode(address)

#_________________________________________________________________________________________________________________________________
#Create Latitude and Longitude Columns

def coordinates(df):
    
    df = df.where((pd.notnull(df)), None)
    df['Localização'] = df['Cidade'].apply(lambda x: do_geocode(x) if x != None else None)
    
    #Create the Latitude Column
    lat=[]
    for i in df['Localização']:
        if i== None:
            lat.append(None)
        else:
            lat.append(i.latitude)
    df['Latitude']=lat
    df['Latitude'].astype('float')

    #Create the Longitude Column
    long=[]
    for i in df['Localização']:
        if i== None:
            long.append(None)
        else:
            long.append(i.longitude)
    df['Longitude']=long
    df['Longitude'].astype('float')

    return df

#_________________________________________________________________________________________________________________________________
#Mapa Function

def map_function(df):
    df = df.dropna(subset=['Latitude'])
    mapa = folium.Map(location=[df['Latitude'][0] ,df['Longitude'][0]],
    #tiles = 'cartodbpositron', #tiles muda o tipo de mapa
          zoom_start=9, 
          control_scale=True)

    locations = df[['Latitude', 'Longitude']]
    locationlist = locations.values.tolist()
    
    
    for point in range(len(locationlist)):
        
        folium.Marker(location = locationlist[point],
                      #Informações a serem apresentadas ao clicar no pop-up:
                      #popup = dfsave['Cidade'][point],
                      icon=folium.Icon(color='orange', prefix='fa', icon_color='white',icon='fa-sun-o')
                 ).add_to(mapa)  
    
    return mapa.save('mapa.html')

#_________________________________________________________________________________________________________________________________

if __name__ == "__main__":

    #Reading and processing data::
    
    df = data_reading()
    df = coordinates(df)
    df_coordenadas = df[['Localização','Latitude','Longitude']]
    df_coordenadas = df_coordenadas[~df_coordenadas.astype(str).eq('None').any(1)]
    
    #Creating map:
    map_function(df_coordenadas)
