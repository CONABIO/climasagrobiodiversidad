from pydoc import visiblename
from re import search
import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
from dash import Dash, html, dcc, Input, Output, dash_table, ctx
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
from flask import send_from_directory
from flask import Flask, request
import dash_bootstrap_components as dbc

server = Flask(__name__)

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
df_taxons = df_taxons.drop(df_taxons['taxon'].loc[df_taxons['taxon']=='Zea mays subsp. mexicana raza Durango'].index)
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
df_taxons = df_taxons.drop(df_taxons['taxon simple'].loc[df_taxons['taxon simple']=='teocintle subespecie mexicana'].index)
df_taxons = df_taxons.drop(df_taxons['taxon simple'].loc[df_taxons['taxon simple']=='teocintle subespecie parviglumis'].index)
df_taxons = df_taxons.reset_index(drop=True)

def make_layout ():
    host = flask.request.host_url if flask.has_request_context() else ''
    return html.Div([
        dcc.Location(id='url', refresh=False),
        dbc.NavbarSimple(
            
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="https://app-siagro.conabio.gob.mx/maices/", style={'padding-left':'10px','margin-top':'5px','margin-bottom':'5px'})),
                dbc.NavItem(dbc.NavLink("Mapa", href="/", active=True, style={'padding-left':'10px','margin-top':'5px','margin-bottom':'5px',})),
                dbc.NavItem(dbc.NavLink("Ayuda", href="https://app-siagro.conabio.gob.mx/maices#ayuda/", style={'padding-left':'10px','margin-top':'5px','margin-bottom':'5px'})),
                dbc.NavItem(dbc.NavLink("Créditos", href="https://app-siagro.conabio.gob.mx/maices#creditos/", style={'padding-left':'10px','margin-top':'5px','margin-bottom':'5px'})),
                
            ],
            color="dark",
            dark=True,
            fixed= "top",
            class_name="pill",
            links_left=True,
        ),
        html.Div([
            html.H2('Condiciones climáticas de las razas de maíz en México', style={'textAlign': 'center', 'color': '#343a40', 'font-family': ['system-ui','-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol']}),
            html.Div(dcc.Dropdown(df_taxons['taxon simple'].unique(), id='pandas-dropdown-2', placeholder='Selecciona un tipo de maiz'),style={'margin-top':'20px','cursor':'pointer'}),
            dcc.RadioItems(
                options=[
                {'label' : ' Altitud ', 'value' : 'altitud'},
                {'label' : ' Temperatura ', 'value' : 'temperatura'},
                {'label' : ' Precipitación ', 'value' : 'precipitacion'},
                ], value='altitud', id='radio-conditions', style={'textAlign':'center','margin-top':'20px'}),
            dcc.Graph(id='mapa'),
            html.H3('Distribución de los puntos de colecta sobre las condiciones ambientales:', style={'textAlign': 'center', 'color': '#343a40','margin-top':'20px','font-family': ['system-ui','-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol']}),
            dcc.Graph(id='strip'),
        ],style={'background-color':'rgba(254, 254, 255, 0.7)','padding':'30px'}),
        
    dcc.Loading(id= 'loading-1', type='dot', 
    children=html.Div(id='loading-output-1',style={'background-color':'#2A3C24','padding':'30px', 'color': 'white'}), 
    fullscreen= True),
    html.Div([
                'Aquí presentamos 10 localidades con sus condiciones, pero puedes descargar las localidades completas dando clic en el botón: ',
                html.Br(),
                html.Br(),
                html.Div(dbc.Button("Descargar tabla completa", color="dark", id="btn_csv", className="me-1", n_clicks=0), className="d-grid gap-2 col-6 mx-auto"),
                dcc.Store(id='intermediate-value'),
                dcc.Download(id="download-dataframe-csv"),],id='divButton', style={'background-color':'#2A3C24','padding':'30px','padding-top':'0px', 'color': 'white', 'display': 'none' }),
    
    html.Div(id='pandas-output-container-2',style={'background-color':'#2A3C24','padding':'30px', 'padding-top':'0px','color': 'white'}),
    dcc.Loading(id= 'loading-2', type='dot', 
    children=html.Div(id='loading-output-2',style={'background-color':'#2A3C24','padding':'30px', 'color': 'rgb(42, 60, 36)'}), 
    fullscreen= True)
],style={'background-image':'url("/assets/focales.jpg")','width':'102%','height':'100%','background-attachment': 'fixed','margin-top':'5px','margin-left':'-10px','margin-bottom':'-10px', 'padding-top':'50px'})

app = Dash(server=server,external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Mapa SIAgro' 
app.layout = make_layout

@app.callback(Output("url", "pathname"), [Input("pandas-dropdown-2", "value"),Input('url', 'pathname')])
def update_url_on_dropdown_change(dropdown_value,pathname):

    if pathname != "/" and dropdown_value is None:
        pathname=pathname[0:]
        url_taxon=pathname
    if pathname=="/":
        url_taxon=''
    if dropdown_value is not None:
        taxon_id=df_taxons.loc[df_taxons['taxon simple']== dropdown_value, 'taxon_id'].values[0]
        url_taxon='id='+taxon_id
    
    return url_taxon

@app.callback(Output('intermediate-value', 'data'),Output("divButton", "style"),Output('pandas-dropdown-2', 'value'),Output("loading-output-1", "children"),Output("pandas-output-container-2","children"), [Input("btn_csv", "n_clicks"),Input("pandas-dropdown-2", "value"),Input('url', 'pathname')],prevent_initial_call=True,)

#Función para el texto y la tabla 
def update_output(n_clicks,value,pathname):
    if (value is not None) or (value is None and pathname!=""):
        if pathname=='/':
            taxon_id=df_taxons.loc[df_taxons['taxon simple']== value, 'taxon_id'].values[0]
        else:
            taxon_id=pathname[4:]
        new_query = '{\n  taxons(pagination:{limit:1} search:{field:taxon_id value:"%' + taxon_id +'%" operator:iLike}){\n    taxon_id\n    taxon\n    registroConnection(pagination:{first:1000}){\n      edges{\n        node{\n          id\n          sitio{\n            altitud\n            estado\n            municipio\n            localidad\n            condiciones_sitioFilter(pagination:{limit:2} search:{field:nombre_corto value:"%t3gw%" operator:iLike}){\n              sitio_id\n              condicion\n              valor\n              unidad\n              nombre_corto\n              fuente\n            }\n          }\n          caracteristicas_cualitativasFilter(pagination:{limit:10} search:{field:nombre_corto value:"color_grano" operator:eq }){\n            nombre_corto\n            valor\n          }\n          caracteristicas_cuantitativasFilter(pagination:{limit:10}\n                search: {operator: or,\n                         search: [{field: nombre_corto,\n                          value: "hileras_mazorca",\n                          operator: eq},\n                            {field: nombre_corto,\n                             value: "longitud_mazorca",\n                             operator: eq}]\n                                                          }){\n                 nombre_corto\n                 valor\n          }\n          }\n        }\n      }\n    }\n  }\n'
        result= run_query(url, new_query, statusCode)    
        complete_dict=[]
        value = result['data']['taxons'][0]['taxon']
        value = value.replace("Zea mays subsp. mays", "maíz")
        value = value.replace("Zea mays subsp. mexicana", "teocintle subespecie mexicana")
        value = value.replace("Zea mays subsp. parviglumis", "teocintle subespecie parviglumis")
        for i in range (len(result['data']['taxons'][0]['registroConnection']['edges'])):
            sitio = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']
            if len(result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter']) == 0:
                sitio['precipitacion'] = np.nan
                sitio['temperatura'] = np.nan
            else:
                sitio['temperatura'] = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter'][0]['valor']
                sitio['precipitacion'] = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter'][1]['valor']
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
                sitio['longitud_promedio']=hileras_mazorca
            elif len (result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cuantitativasFilter']) == 1:
                sitio['hileras_mazorca']=result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cuantitativasFilter'][0]['valor']
                sitio['longitud_promedio']='no disponible'
            elif len (result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cuantitativasFilter']) == 2:
                sitio['hileras_mazorca']=result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cuantitativasFilter'][0]['valor']
                sitio['longitud_promedio']=result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['caracteristicas_cuantitativasFilter'][1]['valor']
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
            min_precipitacion = round(df['precipitacion'].min())
            max_precipitacion = round(df['precipitacion'].max())

        hileras = df[df.hileras_mazorca != 'no disponible']
        if len(hileras) !=0:
            promedio_hileras = round(hileras['hileras_mazorca'].mean())
        else:
            promedio_hileras = '(no disponible)'
        
        longitud = df[df.longitud_promedio != 'no disponible']
        if len(longitud) !=0:
            promedio_longitud = round(longitud['longitud_promedio'].mean())
        else:
            promedio_longitud = '(no disponible)'

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

        if len(colores_maices) == 11 and promedio_hileras == '(no disponible)' and promedio_longitud == '(no disponible)':
            texto = ''
        elif len(colores_maices) == 11 and promedio_hileras != '(no disponible)' and promedio_longitud != '(no disponible)':
            texto = f'En esta raza se han encontrado mazorcas que en promedio tienen {promedio_hileras} hileras por mazorca y una longitud de {promedio_longitud} cm.'
        elif len(colores_maices) != 11 and promedio_hileras != '(no disponible)' and promedio_longitud != '(no disponible)':
            texto = f'En esta raza se han encontrado {colores_maices}; en mazorcas que en promedio tienen {promedio_hileras} hileras por mazorca y una longitud de {promedio_longitud} cm.'
        elif len(colores_maices) != 11 and promedio_hileras == '(no disponible)' and promedio_longitud != '(no disponible)':  
            texto = f'En esta raza se han encontrado {colores_maices} y una longitud de {promedio_longitud} cm.'
        elif len(colores_maices) != 11 and promedio_hileras == '(no disponible)' and promedio_longitud == '(no disponible)':  
            texto = f'En esta raza se han encontrado {colores_maices}.'

        df= df.round() 

        lista=[]
        encabezados=[]

        for i in range(0,10):
            encabezado=df['estado'][i] + ", " + df['municipio'][i] + ", " + df['localidad'][i].upper()
            aux = pd.DataFrame(
                {
                    "Condición": ["Altitud", "Temperatura", "Precipitación"],
                    "Medida": [[df['altitud'][i], " msnm"], [df['temperatura'][i], " °C"] , [df['precipitacion'][i], " mm"] ],
                    "Categoría": [df['cat_altitud'][i], df['cat_temperatura'][i], df['cat_precipitacion'][i]],
                }
            )

            lista.append(aux)
            encabezados.append(encabezado)

        return (df.to_json(date_format='iso', orient='split')),{'background-color':'#2A3C24','padding':'30px','padding-top':'0px', 'color': 'white','display': 'block'},value, (dcc.Markdown (f'''El {value} se cultiva en general en tierras {escala_altitud} desde {min_altitud:,} hasta {max_altitud:,} metros sobre el nivel del mar (msnm). 
        Se cultiva en lugares donde durante la época de temporal la temperatura es {escala_temperatura}, con temperaturas que van desde {min_temperatura} °C hasta {max_temperatura} 
        ºC y donde las lluvias son {escala_precipitacion}, con cantidades que van desde {min_precipitacion} mm hasta {max_precipitacion} mm.'''), 
        dcc.Markdown(
            f'''{texto}'''
        )), (dcc.Markdown(
            f'''**{encabezados[0]}**'''),
            dbc.Table.from_dataframe(lista[0], striped=True, bordered=True, hover=True, style={'background-color':'white'}),
            dcc.Markdown(
            f'''**{encabezados[1]}**'''),
            dbc.Table.from_dataframe(lista[1], striped=True, bordered=True, hover=True, style={'background-color':'white'}),
            dcc.Markdown(
            f'''**{encabezados[2]}**'''),
            dbc.Table.from_dataframe(lista[2], striped=True, bordered=True, hover=True, style={'background-color':'white'}),
            dcc.Markdown(
            f'''**{encabezados[3]}**'''),
            dbc.Table.from_dataframe(lista[3], striped=True, bordered=True, hover=True, style={'background-color':'white'}),
            dcc.Markdown(
            f'''**{encabezados[4]}**'''),
            dbc.Table.from_dataframe(lista[4], striped=True, bordered=True, hover=True, style={'background-color':'white'}),
            dcc.Markdown(
            f'''**{encabezados[5]}**'''),
            dbc.Table.from_dataframe(lista[5], striped=True, bordered=True, hover=True, style={'background-color':'white'}),
            dcc.Markdown(
            f'''**{encabezados[6]}**'''),
            dbc.Table.from_dataframe(lista[6], striped=True, bordered=True, hover=True, style={'background-color':'white'}),
            dcc.Markdown(
            f'''**{encabezados[7]}**'''),
            dbc.Table.from_dataframe(lista[7], striped=True, bordered=True, hover=True, style={'background-color':'white'}),
            dcc.Markdown(
            f'''**{encabezados[8]}**'''),
            dbc.Table.from_dataframe(lista[8], striped=True, bordered=True, hover=True, style={'background-color':'white'}),
            dcc.Markdown(
            f'''**{encabezados[9]}**'''),
            dbc.Table.from_dataframe(lista[9], striped=True, bordered=True, hover=True, style={'background-color':'white'})
            )
    else:
        texto="Selecciona una raza en el menú desplegable al inicio de la página"
        texto2=""
        dftest = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})

        return (dftest.to_json(date_format='iso', orient='split')),{'display': 'none'},value, dcc.Markdown(f'''{texto}'''),dcc.Markdown(f'''{texto2}''')       
    

@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input('intermediate-value', 'data'),Input("btn_csv", "n_clicks"),Input("pandas-dropdown-2", "value"),],
    prevent_initial_call=True,
)
def func(data,n_clicks,value):
    #dftest = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})
    dff = pd.read_json(data, orient='split')
    #print("*************",n_clicks)
    if "btn_csv" == ctx.triggered_id:
        dff['raza']=value
        dff = dff[['raza','estado','municipio','localidad','altitud','precipitacion','temperatura','color_grano','hileras_mazorca','longitud_promedio','cat_altitud','cat_temperatura','cat_precipitacion']]
        dff = pd.concat([dff[col].astype(str).str.lower() for col in dff.columns], axis=1)
        nombre=value+".csv"
        return (dcc.send_data_frame(dff.to_csv, nombre,index=False))
    #return "hola"
    #return dcc.send_data_frame(dff.to_csv, "test.csv",index=False)
    
    
    

@app.callback(
    Output(component_id='mapa', component_property='figure'),
    Output(component_id='strip', component_property='figure'),
    Output(component_id='loading-output-2', component_property='children'),
    [Input(component_id='pandas-dropdown-2', component_property='value'),
    Input(component_id='radio-conditions', component_property='value'),
    Input('url', 'pathname')]
)


#Función para el mapa 
def update_map(column_chosen, condition_chosen, pathname):
    #print("column_chosen",column_chosen)
    if condition_chosen == 'altitud':
        image = '/var/www/FlaskApp/FlaskApp/altitud.png'
        color_scale = 'turbid'
        x_max = 3400
    elif condition_chosen == 'temperatura':
        image = '/var/www/FlaskApp/FlaskApp/temperatura.png'
        color_scale = 'balance'
        x_max = 40
    elif condition_chosen == 'precipitacion':
        image = '/var/www/FlaskApp/FlaskApp/precipitacion.png'
        color_scale = 'YlGnBu'
        x_max = 1500
    x_min= 0
    fondo = base64.b64encode(open(image, 'rb').read())

    if column_chosen is None:
        #print("entro a is none")
        complete_dict={"lat": "0","lon": "0"}
        #df = pd.DataFrame.from_dict([complete_dict])
        fig1 = px.scatter_mapbox(lat=['21.826080'],lon=['-101.460875'],zoom=4, height=500,color_discrete_sequence=['black'])
        
        fig1.update_layout(mapbox_style="carto-darkmatter")#stamen-terrain, carto-positron, open-street-map, carto-darkmatter
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig1.update_layout(height= 300)
        fig1.update_coloraxes(showscale=False)
        fig2 = px.scatter(x=[0], y=[1],color_discrete_sequence=['white']) 
        fig2.update_layout(margin={"r":20,"t":40,"l":20,"b":40})
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

        return fig1, fig2, pathname

    if column_chosen is not None:
        #print("entro a not none")
        
        #if taxon url tiene algo entonces taxon id tiene ese valor y si no es el column chosen
        if pathname=='/':
            taxon_id=df_taxons.loc[df_taxons['taxon simple']== column_chosen, 'taxon_id'].values[0]
        else:
            taxon_id=pathname[4:]

        new_query = '{\n  taxons(pagination:{limit:1} search:{field:taxon_id value:"%' + taxon_id + '%" operator:iLike}){\n    taxon_id\n    taxon\n    registroConnection(pagination:{first:1000}){\n      edges{\n        node{\n          id\n          sitio{\n            latitud\n            longitud\n            altitud\n            estado\n            municipio\n            localidad\n            condiciones_sitioFilter(pagination:{limit:2}search:{field:nombre_corto value:"%t3gw%" operator:iLike}){\n              sitio_id\n              condicion\n              valor\n              unidad\n              nombre_corto\n              fuente\n            }\n          }\n        }\n        }\n      }\n    }\n  } '
        result= run_query(url, new_query, statusCode)    
        complete_dict=[]
        for i in range (len(result['data']['taxons'][0]['registroConnection']['edges'])):
            sitio = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']
            if len(result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter']) == 0:
                sitio['precipitacion'] = np.nan
                sitio['temperatura'] = np.nan
            else:
                sitio['temperatura'] = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter'][0]['valor']
                sitio['precipitacion'] = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']['condiciones_sitioFilter'][1]['valor']
            del sitio['condiciones_sitioFilter']
            complete_dict.append(sitio)
        df = pd.DataFrame.from_dict(complete_dict)
        fig1 = px.scatter_mapbox(df, lat="latitud", lon="longitud", hover_data={'latitud':False, 'longitud':False, 'municipio':True}, color = condition_chosen,
                                color_continuous_scale=color_scale, zoom=4, height=500, range_color = (x_min, x_max))
        fig1.update_layout(mapbox_style="carto-darkmatter")#stamen-terrain, carto-positron, open-street-map, carto-darkmatter
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig1.update_layout(height= 300)
        fig1.update_coloraxes(showscale=False)

        random_num = []
        random.seed(0)
        for i in range(len(df)):
            random_num.append(random.uniform(0.7, 1.5))

        df['random']=random_num

        fig2 = px.scatter(df, x=condition_chosen, y="random", hover_data={'random':False, 'municipio':True},range_x= (x_min, x_max), range_y = (0.3, 2), color_discrete_sequence=n_colors('rgb(0, 0, 0)', 'rgb(255, 255, 255)', 4, colortype = 'rgb')) 

        #fig2 = px.strip(df, x=condition_chosen, stripmode='group', range_x= (x_min, x_max), color_discrete_sequence=n_colors('rgb(0, 0, 0)', 'rgb(255, 255, 255)', 4, colortype = 'rgb'))
        fig2.update_layout(margin={"r":20,"t":40,"l":20,"b":40})
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
        return fig1, fig2, pathname

'''


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    dftest = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})

    return dcc.send_data_frame(dftest.to_csv, "test.csv",index=False)
'''

if __name__ == "__main__":
    app.run(ssl_context='adhoc')
