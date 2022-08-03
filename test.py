import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
from dash_extensions.javascript import assign
from dash import Dash, html, dcc, Input, Output

colorscale = ['red', 'yellow', 'green', 'blue', 'purple']  # paleta de colores
chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"  # libreria js para colores 
color_prop = 'altitudmapa' #variable para determinar color 

df = pd.read_csv("maices.csv")  
df1 = df[df['especievalida'] == 'Zea mays mays Comiteco']  # seleccion de un taxon
df1 = df1[['latitud', 'longitud', 'estadomapa', 'localidad', color_prop]]  # seleccion de variables
dicts = df1.to_dict('rows')
for item in dicts:
    item["tooltip"] = "{} ({:.1f})".format(item['localidad'], item[color_prop])  
geojson = dlx.dicts_to_geojson(dicts, lat = 'latitud', lon="longitud")  # conversion a geojson
geobuf = dlx.geojson_to_geobuf(geojson)  # conversion a  geobuf
# Creacion barra de color
vmax = df[color_prop].max()
colorbar = dl.Colorbar(colorscale=colorscale, width=20, height=150, min=0, max=vmax, unit='m')
# Geojson rendering logic, must be JavaScript as it is executed in clientside.
point_to_layer = assign("""function(feature, latlng, context){
    const {min, max, colorscale, circleOptions, colorProp} = context.props.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
    circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop.
    return L.circleMarker(latlng, circleOptions);  // sender a simple circle marker.
}""")
# Creacion geojson.
geojson = dl.GeoJSON(data=geobuf, id="geojson", format="geobuf",
                     zoomToBounds=True,  # when true, zooms to bounds when data changes
                     options=dict(pointToLayer=point_to_layer),  # how to draw points
                     superClusterOptions=dict(radius=50),   # adjust cluster size
                     hideout=dict(colorProp=color_prop, circleOptions=dict(fillOpacity=1, stroke=False, radius=5),
                                  min=0, max=vmax, colorscale=colorscale))

# Creacion de app 
app = Dash(external_scripts=[chroma], prevent_initial_callbacks=True)
app.layout = html.Div([
    html.H1('Maices en México', style={'textAlign': 'center', 'color': '#1A1A1A'}),
    dl.Map([dl.TileLayer(), geojson, colorbar]),
    dcc.Dropdown(df.especievalida.unique(), id='pandas-dropdown-2', placeholder= 'Selecciona taxon', multi=True),
    html.Div(id='pandas-output-container-2')
], style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block", "position": "relative"})


@app.callback(
    Output('pandas-output-container-2', 'children'),
    Input('pandas-dropdown-2', 'value')
)
def update_output(value):
    return f'Seleccionaste el taxon {value}'

if __name__ == '__main__':
    app.run_server()