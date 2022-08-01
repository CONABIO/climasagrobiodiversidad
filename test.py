import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
from dash_extensions.javascript import assign
from dash import Dash, html

colorscale = ['red', 'yellow', 'green', 'blue', 'purple']  # paleta de colores
chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"  # libreria js para colores 
color_prop = 'altitudmapa' #variable para determinar color 

df = pd.read_csv("maices.csv")  
df = df[df['especievalida'] == 'Zea mays mays Comiteco']  # seleccion de un taxon
df = df[['latitud', 'longitud', 'estadomapa', 'localidad', color_prop]]  # seleccion de variables
dicts = df.to_dict('rows')
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
    dl.Map([dl.TileLayer(), geojson, colorbar]),
], style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block", "position": "relative"})

if __name__ == '__main__':
    app.run_server()