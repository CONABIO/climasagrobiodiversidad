from pydoc import visiblename
from re import search
import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
from dash import Dash, html, dcc, Input, Output, dash_table
import requests
import urllib3
urllib3.disable_warnings()
import base64
import time
import plotly.express as px
import flask
from plotly.colors import n_colors
import numpy as np
import math 
import random
#from selenium import webdriver
#from selenium.webdriver import FirefoxOptions

#opts = FirefoxOptions()
#opts.add_argument("--headless")

#Query para obtener cada uno de los distintos taxones
my_query= """{
  taxons(pagination:{limit:200} search:{field:estatus value:"aceptado" operator:eq}){
    taxon
    taxon_id
    categoria
    estatus
  }
}
"""
url="https://maices-siagro.conabio.gob.mx/api/graphql"
statusCode = 200

def run_query(uri, query, statusCode):
    request = requests.post(uri, json={'query': query}, verify=False)
    if request.status_code == statusCode:
        return request.json()
    else:
        raise Exception(f"Unexpected status code returned: {request.status_code}")


result = run_query(url, my_query, statusCode)

taxons = []
for i in range (len(result['data']['taxons'])):
    taxons.append(result['data']['taxons'][i])

df_taxons=pd.DataFrame.from_dict(taxons)

# Se eliminan taxones repetidos
df_taxons = df_taxons.drop(df_taxons['taxon'].loc[df_taxons['taxon']=='Zea mays'].index)
df_taxons = df_taxons.drop(df_taxons['taxon'].loc[df_taxons['taxon']=='Zea mays subsp. mays'].index)
df_taxons = df_taxons.reset_index(drop=True)

def change_taxon (x):
    if x.startswith('Zea mays subsp. mays'):
        start = 'Zea mays subsp. mays'
        y = 'maíz' + x[len(start):]
    elif x.startswith('Zea mays subsp. mexicana'):
        start = 'Zea mays subsp. mexicana'
        y = 'teocintle subespecie mexicana' + x[len(start):]
    elif x.startswith('Zea mays subsp. parviglumis'):
        start = 'Zea mays subsp. parviglumis'
        y = 'teocintle subespecie parviglumis' + x[len(start):]
    return y

df_taxons['taxon simple']=df_taxons['taxon'].apply(change_taxon)

#image= 'fondo.png'
#fondo = base64.b64encode(open(image, 'rb').read())

def make_layout ():
    host = flask.request.host_url if flask.has_request_context() else ''
    return html.Div([
    html.H1('Maices en México', style={'textAlign': 'center', 'color': '#1A1A1A'}),
    dcc.Graph(id='mapa'),
    dcc.Graph(id='strip'),
    dcc.Location(id='url', refresh=False),
    dcc.Dropdown(df_taxons['taxon simple'].unique(), 'maíz raza Blando de Sonora', id='pandas-dropdown-2', placeholder='Selecciona un tipo de maiz'),
    dcc.RadioItems([
        {'label' : 'Altitud', 'value' : 'altitud'},
        {'label' : 'Temperatura', 'value' : 'temperatura'},
        {'label' : 'Precipitación', 'value' : 'precipitacion'}
    ], 'altitud', id='radio-conditions'),
    dcc.Loading(id= 'loading-1', type='dot', children=html.Div(id='loading-output-1'), fullscreen= True),
    html.Div(id='pandas-output-container-2')
])

app = Dash(__name__)
app.layout = make_layout
#app.layout = html.Div([
 #   html.H1('Maices en México', style={'textAlign': 'center', 'color': '#1A1A1A'}),
 #   dcc.Graph(id='mapa'),
 #   dcc.Graph(id='strip'),
 #   dcc.Location(id='url', refresh=True),
 #   dcc.Dropdown(df_taxons['taxon simple'].unique(), 'maíz raza Blando de Sonora', id='pandas-dropdown-2', placeholder='Selecciona un tipo de maiz'),
 #   dcc.RadioItems([
 #       {'label' : 'Altitud', 'value' : 'altitud'},
 #       {'label' : 'Temperatura', 'value' : 'temperatura'},
 #       {'label' : 'Precipitación', 'value' : 'precipitacion'}
 #   ], 'altitud', id='radio-conditions'),
 #   dcc.Loading(id= 'loading-1', type='dot', children=html.Div(id='loading-output-1'), fullscreen= True),
 #   html.Div(id='pandas-output-container-2')
#])

@app.callback(
    Output('pandas-output-container-2', 'children'),
    [Input('url', 'pathname')])
def callback_func(pathname):
    # here you can use the pathname however, just like a normal function input
    print('hola')

@app.callback(Output("url", "pathname"), Input("pandas-dropdown-2", "value"))
def update_url_on_dropdown_change(dropdown_value):
    taxon_id=df_taxons.loc[df_taxons['taxon simple']== dropdown_value, 'taxon_id'].values[0]
    url_taxon='?id='+taxon_id
    print(flask.request.base_url)
    return url_taxon

@app.callback(Output("loading-output-1", "children"), [Input("pandas-dropdown-2", "value")])

#Función para el texto y la tabla 
def update_output(value):
    taxon_id=df_taxons.loc[df_taxons['taxon simple']== value, 'taxon_id'].values[0]
    new_query = '{\n  taxons(pagination:{limit:1} search:{field:taxon_id value:"%' + taxon_id +'%" operator:iLike}){\n    taxon_id\n    taxon\n    registroConnection(pagination:{first:1000}){\n      edges{\n        node{\n          id\n          sitio{\n            altitud\n            estado\n            municipio\n            localidad\n            condiciones_sitioFilter(pagination:{limit:2}){\n              sitio_id\n              condicion\n              valor\n              unidad\n              nombre_corto\n              fuente\n            }\n          }\n          caracteristicas_cualitativasFilter(pagination:{limit:10} search:{field:nombre_corto value:"color_grano" operator:eq }){\n            nombre_corto\n            valor\n          }\n          caracteristicas_cuantitativasFilter(pagination:{limit:10} search:{field:nombre_corto value:"hileras_mazorca" operator:eq }){\n            nombre_corto\n            valor\n          }\n          }\n        }\n      }\n    }\n  } '
    result= run_query(url, new_query, statusCode)    
    complete_dict=[]
    for i in range (len(result['data']['taxons'][0]['registroConnection']['edges'])):
        sitio = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']
        if len(result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter']) == 0:
            sitio['precipitacion'] = np.nan
            sitio['temperatura'] = np.nan
        else:
            sitio['precipitacion'] = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter'][0]['valor']
            sitio['temperatura'] = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter'][1]['valor']
        if len (result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cualitativasFilter']) == 0:
            color_grano = 'no disponible'
            sitio['color_grano']=color_grano
        else:
            colores = []
            for j in range (len(result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cualitativasFilter'])):
                #colores = colores +result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cualitativasFilter'][j]['valor'] + ', '
                colores.append(result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cualitativasFilter'][j]['valor'])
            sitio['color_grano']=colores
        if len (result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cuantitativasFilter']) == 0:
            hileras_mazorca = 'no disponible'
            sitio['hileras_mazorca']=hileras_mazorca
        else:
            sitio['hileras_mazorca']=result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cuantitativasFilter'][0]['valor']
        del sitio['condiciones_sitioFilter']
        complete_dict.append(sitio)
    df = pd.DataFrame.from_dict(complete_dict) 
    mean_altitud = df['altitud'].mean() 
    def altitud (x):
        if x < 1200:
            escala_altitud = 'baja'
        elif 1200 <= x < 1800:
            escala_altitud = 'mediana altitud'
        else:
            escala_altitud = 'alta'
        return escala_altitud
    df['cat_altitud']= df['altitud'].apply(altitud)
    escala_altitud = altitud(mean_altitud)
   
    min_altitud = df['altitud'].min()
    max_altitud = df['altitud'].max()
    
    mean_temperatura = df['temperatura'].mean() 
    def temperatura (x):
        if x < 18:
            escala_temperatura = 'fría'
        elif 18 <= x <= 21:
            escala_temperatura = 'templada'
        elif 21 < x <= 25:
            escala_temperatura = 'semi-caliente'
        elif 25 < x <= 27:
            escala_temperatura = 'caliente'
        else:
            escala_temperatura = 'muy caliente'
        return escala_temperatura
    df['cat_temperatura']= df['temperatura'].apply(temperatura)
    escala_temperatura = temperatura(mean_temperatura)
    
    if df['temperatura'].isnull().sum() == len(df['temperatura']): 
        min_temperatura = '(no disponible)'
        max_temperatura = '(no disponible)'
        escala_temperatura= '(no disponible)'
    else:
        min_temperatura = round(df['temperatura'].min())
        max_temperatura = round(df['temperatura'].max())

    mean_precipitacion = df['precipitacion'].mean() 
    def precipitacion (x):
        if x < 450:
            escala_precipitacion = 'escasas'
        elif 450 <= x <= 650:
            escala_precipitacion = 'poco abundantes'
        elif 650 < x <= 850:
            escala_precipitacion = 'intermedias'
        elif 850 < x <= 1360:
            escala_precipitacion = 'abundantes'
        else:
            escala_precipitacion = 'muy abundantes'
        return escala_precipitacion
    df['cat_precipitacion']= df['precipitacion'].apply(precipitacion)
    escala_precipitacion = precipitacion(mean_precipitacion)

    if df['precipitacion'].isnull().sum() == len(df['precipitacion']): 
        min_precipitacion = '(no disponible)'
        max_precipitacion = '(no disponible)'
        escala_precipitacion= '(no disponible)'
    else:
        min_precipitacion = round(df['temperatura'].min())
        max_precipitacion = round(df['temperatura'].max())

    hileras = df[df.hileras_mazorca != 'no disponible']
    if len(hileras) !=0:
        promedio_hileras = round(hileras['hileras_mazorca'].mean())
    else:
        promedio_hileras = '(no disponible)'

    color_maices = df['color_grano']
    colores = []
    for i in color_maices:
        if len (i) ==1:
            colores.append(i[0])
        else:
            for j in range (len(i)):
                colores.append(i[j])
    
    mylist = list(set(colores))
    colores_maices = 'los colores: '
    for i in range (len (mylist)):
        color = str(mylist[i])
        if color == 'no disponible':
            continue
        if len(color) <4:
            continue
        colores_maices = colores_maices + color + ', '
    colores_maices =colores_maices[:-2]

    if len(colores_maices) == 11 and promedio_hileras == '(no disponible)':
        texto = 'En esta raza se ha encontrado una longitud de [promedio_longitud] cm.'
    elif len(colores_maices) == 11 and promedio_hileras != '(no disponible)':
        texto = f'En esta raza se han encontrado mazorcas que en promedio tienen {promedio_hileras} hileras por mazorca y una longitud de [promedio_longitud] cm.'
    elif len(colores_maices) != 11 and promedio_hileras != '(no disponible)':
        texto = f'En esta raza se han encontrado {colores_maices}; en mazorcas que en promedio tienen {promedio_hileras} hileras por mazorca y una longitud de [promedio_longitud] cm.'
    elif len(colores_maices) != 11 and promedio_hileras == '(no disponible)':  
        texto = f'En esta raza se han encontrado {colores_maices} y una longitud de [promedio_longitud] cm.'


    df= df.round() 

    return dcc.Markdown (f'''El {value} se cultiva en general en tierras {escala_altitud} desde {min_altitud:,} hasta {max_altitud:,} metros sobre el nivel del mar (msnm). 
    Se cultiva en lugares donde durante la época de temporal la temperatura es {escala_temperatura}, con temperaturas que van desde {min_temperatura} °C hasta {max_temperatura} 
    ºC y donde las lluvias son {escala_precipitacion}, con cantidades que van desde {min_precipitacion} mm hasta {max_precipitacion} mm.'''), dcc.Markdown(
        f'''{texto}'''
    ), dcc.Markdown(
        f'''
        **{df['estado'][0]}**, **{df['municipio'][0]}**, **{df['localidad'][0]}**

        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][0]:,} msnm  | ({df['cat_altitud'][0]}) |
        | *Temperatura*       |  {(df['temperatura'][0])} °C  |  ({df['cat_temperatura'][0]})   |
        | *Precipitación*       | {df['precipitacion'][0]} mm  |  ({df['cat_precipitacion'][0]})   |

        **{df['estado'][1]}**, **{df['municipio'][1]}**, **{df['localidad'][1]}** 

        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][1]:,} msnm  | ({df['cat_altitud'][1]}) |
        | *Temperatura*       |  {df['temperatura'][1]} °C  |  ({df['cat_temperatura'][1]})   |
        | *Precipitación*       | {df['precipitacion'][1]} mm  |  ({df['cat_precipitacion'][1]})   |

        **{df['estado'][2]}**, **{df['municipio'][2]}**, **{df['localidad'][2]}**

        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][2]:,} msnm  | ({df['cat_altitud'][2]}) |
        | *Temperatura*       |  {df['temperatura'][2]} °C  |  ({df['cat_temperatura'][2]})   |
        | *Precipitación*       | {df['precipitacion'][2]} mm  |  ({df['cat_precipitacion'][2]})   |

        **{df['estado'][3]}**, **{df['municipio'][3]}**, **{df['localidad'][3]}**  
        
        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][3]:,} msnm  | ({df['cat_altitud'][3]}) |
        | *Temperatura*       |   {df['temperatura'][3]} °C  |  ({df['cat_temperatura'][3]})   |
        | *Precipitación*       | {df['precipitacion'][3]} mm  |  ({df['cat_precipitacion'][3]})   |

        **{df['estado'][4]}**, **{df['municipio'][4]}**, **{df['localidad'][4]}**

        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][4]:,} msnm  | ({df['cat_altitud'][4]}) |
        | *Temperatura*       |   {df['temperatura'][4]} °C  |  ({df['cat_temperatura'][4]})   |
        | *Precipitación*       | {df['precipitacion'][4]} mm  |  ({df['cat_precipitacion'][4]})   |

        **{df['estado'][5]}**, **{df['municipio'][5]}**, **{df['localidad'][5]}**

        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][5]:,} msnm  | ({df['cat_altitud'][5]}) |
        | *Temperatura*       |   {df['temperatura'][5]} °C  |  ({df['cat_temperatura'][5]})   |
        | *Precipitación*       | {df['precipitacion'][5]} mm  |  ({df['cat_precipitacion'][5]})   |

        **{df['estado'][6]}**, **{df['municipio'][6]}**, **{df['localidad'][6]}**     

        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][6]:,} msnm  | ({df['cat_altitud'][6]}) |
        | *Temperatura*       |   {df['temperatura'][6]} °C  |  ({df['cat_temperatura'][6]})   |
        | *Precipitación*       | {df['precipitacion'][6]} mm  |  ({df['cat_precipitacion'][6]})   |

        **{df['estado'][7]}**, **{df['municipio'][7]}**, **{df['localidad'][7]}**     

        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][7]:,} msnm  | ({df['cat_altitud'][7]}) |
        | *Temperatura*       |   {df['temperatura'][7]} °C  |  ({df['cat_temperatura'][7]})   |
        | *Precipitación*       |  {df['precipitacion'][7]} mm  |  ({df['cat_precipitacion'][7]})   |

        **{df['estado'][8]}**, **{df['municipio'][8]}**, **{df['localidad'][8]}**     

        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][8]:,} msnm  | ({df['cat_altitud'][8]}) |
        | *Temperatura*       |   {df['temperatura'][8]} °C  |  ({df['cat_temperatura'][8]})   |
        | *Precipitación*       | {df['precipitacion'][8]} mm  |  ({df['cat_precipitacion'][8]})   |

        **{df['estado'][9]}**, **{df['municipio'][9]}**, **{df['localidad'][9]}** 

        |   Condición  | medida  | categoria |
        | :------------- | :----------: | -----------: |
        |  *Altitud*   |  {df['altitud'][9]:,} msnm  | ({df['cat_altitud'][9]}) |
        | *Temperatura*       |   {df['temperatura'][9]} °C  |  ({df['cat_temperatura'][9]})   |
        | *Precipitación*       | {df['precipitacion'][9]} mm  |  ({df['cat_precipitacion'][9]})   |
        '''
    )
    

@app.callback(
    Output(component_id='mapa', component_property='figure'),
    Output(component_id='strip', component_property='figure'),
    [Input(component_id='pandas-dropdown-2', component_property='value'),
    Input(component_id='radio-conditions', component_property='value')]
)


#Función para el mapa 
def update_map(column_chosen, condition_chosen):
    if condition_chosen == 'altitud':
        image = 'altitud.png'
        color_scale = 'turbid'
        x_max = 3400
    elif condition_chosen == 'temperatura':
        image = 'temperatura.png'
        color_scale = 'RdBu'
        x_max = 40
    elif condition_chosen == 'precipitacion':
        image = 'precipitacion.png'
        color_scale = 'YlGnBu'
        x_max = 1500
    x_min= 0
    fondo = base64.b64encode(open(image, 'rb').read())
    taxon_id=df_taxons.loc[df_taxons['taxon simple']== column_chosen, 'taxon_id'].values[0]
    new_query = '{\n  taxons(pagination:{limit:1} search:{field:taxon_id value:"%' + taxon_id + '%" operator:iLike}){\n    taxon_id\n    taxon\n    registroConnection(pagination:{first:1000}){\n      edges{\n        node{\n          id\n          sitio{\n            latitud\n            longitud\n            altitud\n            estado\n            municipio\n            localidad\n            condiciones_sitioFilter(pagination:{limit:2}){\n              sitio_id\n              condicion\n              valor\n              unidad\n              nombre_corto\n              fuente\n            }\n          }\n        }\n        }\n      }\n    }\n  } '
    result= run_query(url, new_query, statusCode)    
    complete_dict=[]
    for i in range (len(result['data']['taxons'][0]['registroConnection']['edges'])):
        sitio = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']
        if len(result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter']) == 0:
            sitio['precipitacion'] = np.nan
            sitio['temperatura'] = np.nan
        else:
            sitio['precipitacion'] = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter'][0]['valor']
            sitio['temperatura'] = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter'][1]['valor']
        del sitio['condiciones_sitioFilter']
        complete_dict.append(sitio)
    df = pd.DataFrame.from_dict(complete_dict)
    fig1 = px.scatter_mapbox(df, lat="latitud", lon="longitud", hover_data={'latitud':False, 'longitud':False, 'municipio':True}, color = condition_chosen,
                            color_continuous_scale=color_scale, zoom=4, height=500, range_color = (x_min, x_max))
    fig1.update_layout(mapbox_style="carto-darkmatter")#stamen-terrain, carto-positron, open-street-map, carto-darkmatter
    fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig1.update_coloraxes(showscale=False)

    random_num = []
    random.seed(0)
    for i in range(len(df)):
        random_num.append(random.uniform(0.7, 1.5))

    df['random']=random_num

    fig2 = px.scatter(df, x=condition_chosen, y="random", hover_data={'random':False},range_x= (x_min, x_max), range_y = (0.3, 2), color_discrete_sequence=n_colors('rgb(0, 0, 0)', 'rgb(255, 255, 255)', 4, colortype = 'rgb')) 

    #fig2 = px.strip(df, x=condition_chosen, stripmode='group', range_x= (x_min, x_max), color_discrete_sequence=n_colors('rgb(0, 0, 0)', 'rgb(255, 255, 255)', 4, colortype = 'rgb'))
    fig2.update_layout(margin={"r":20,"t":40,"l":40,"b":40})
    fig2.update_layout(height= 200)
    fig2.update_yaxes(showgrid=False, zeroline=False, visible= False)
    fig2.add_layout_image(
        dict(
            source='data:image/png;base64,{}'.format(fondo.decode()),
            xref="paper", yref= 'paper',
            x=0, y=1,
            sizex=1, sizey=1, #sizex, sizey are set by trial and error
            xanchor="left",
            yanchor="top",
            sizing="stretch",
            opacity= 0.9,
            layer="below")
        )    
    return fig1, fig2
    

app.run_server(debug=True, use_reloader=False) 