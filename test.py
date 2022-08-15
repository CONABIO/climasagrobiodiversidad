import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import requests
import urllib3
urllib3.disable_warnings()
import base64
import time
import plotly.express as px


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

image= 'fondo.png'
fondo = base64.b64encode(open(image, 'rb').read())


app = Dash(__name__)
app.layout = html.Div([
    html.H1('Maices en México', style={'textAlign': 'center', 'color': '#1A1A1A'}),
    dcc.Graph(id='mapa'),
    dcc.Graph(id='strip'),
    dcc.Dropdown(df_taxons['taxon'].unique(), 'Zea mays subsp. mays raza Blando de Sonora', id='pandas-dropdown-2', placeholder='Selecciona un taxon'),
    dcc.Loading(id= 'loading-1', type='cube', children=html.Div(id='loading-output-1'), fullscreen= True),
    html.Div(id='pandas-output-container-2')
])

@app.callback(Output("loading-output-1", "children"), Input("pandas-dropdown-2", "value"))
def input_triggers_spinner(column_chosen):
    time.sleep(2)

@app.callback(
    Output('pandas-output-container-2', 'children'),
    Input('pandas-dropdown-2', 'value')
)
def update_output(value):
    return f'Seleccionaste el taxon {value}'

@app.callback(
    Output(component_id='mapa', component_property='figure'),
    Output(component_id='strip', component_property='figure'),
    [Input(component_id='pandas-dropdown-2', component_property='value')]
)


def update_map(column_chosen):
    taxon_id=df_taxons.loc[df_taxons['taxon']== column_chosen, 'taxon_id'].values[0]
    new_query = '{\n  taxons(pagination:{limit:500} search:{field:taxon_id value:"%'+ taxon_id + '%" operator:iLike}){\n    taxon_id\n    taxon\n    registroConnection(pagination:{first:9000}){\n      edges{\n        node{\n          id\n          sitio{\n            latitud\n            longitud\n            altitud\n            estado\n            municipio\n            localidad\n          }\n        }\n      }\n    }\n  }\n}'
    result= run_query(url, new_query, statusCode)    
    complete_dict=[]
    for i in range (len(result['data']['taxons'][0]['registroConnection']['edges'])):
        sitio = result['data']['taxons'][0]['registroConnection']['edges'][i]['node']['sitio']
        complete_dict.append(sitio)
    df = pd.DataFrame.from_dict(complete_dict)
    fig1 = px.scatter_mapbox(df, lat="latitud", lon="longitud", hover_data={'latitud':False, 'longitud':False, 'municipio':True}, color = "altitud",
                            color_discrete_sequence=["fuchsia"], zoom=4, height=500)
    fig1.update_layout(mapbox_style="open-street-map")
    fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig1.update_coloraxes(showscale=False)

    fig2 = px.strip(df, x='altitud', stripmode='overlay', range_x= (0, 3400))
    fig2.update_layout(margin={"r":20,"t":40,"l":40,"b":40})
    fig2.update_layout(height= 150)
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