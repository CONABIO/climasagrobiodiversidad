# Historia de usos y funcionalidades deseadas 

Se busca desarrollar una herramienta que permita la visualización de un mapa interactivo capaz de mostrar el rango de distintas condiciones climáticas dentro de un cultivo o pariente silvestre (diversidad infraespecífica) con las observaciones del SiAgroBD, a fin de comparar las condiciones climáticas entre lugares geográficos de una forma fácil de entender y acceder.


El público objetivo al que se encuentra dirigida esta herramienta es principalmente a personas con conocimiento sobre agrodiversidad que contempla desde organizaciones campesinas, estudiantes rurales agrónomos y campesinos con ciertas habilidades tecnológicas. No obstante, también se busca que esta herramienta sea de utilidad para personas sin conocimiento sobre el tema. 

Las funciones principales con las que contara la herramienta son:
- Mapa interactivo con las ubicaciones de los registros
- Ubicaciones coloreadas con base en caracteristicas ambientales. 
- Filtros relevantes de características morfológicas
- Variables ambientales (temperatura y precipitación)
- Información relevante  sobre la ubicación del usuario (Función mi localidad)
- Resumen dinámico sobre la semilla de interés
- Gráficos de apoyo sobre distribución de condiciones
- Información adicional de la semilla (Donde comprar, contactos relevantes)


## Requerimientos técnicos

La plataforma en la que se desarrollará la herramienta debe ser lo suficientemente robusta para poder manejar sin problemas los datos del SIAgroBD. La aplicación web no solo será para navegadores de computadoras, se tiene como prioridad que el desarrollo se realice con el enfoque que se visualice en dispositivos móviles (celular-tablets) debido a que es la plataforma a la que tienen acceso más personas del público objetivo. 

Se busca poder extraer y presentar la información del raster de temperatura y precipitación, ser capaz de manejar distintas sesiones al mismo tiempo, respuesta rápida y de fácil mantenimiento. 

Los principales requerimientos técnicos son los siguientes:
- Navegación en dispotivos móviles
- Respuesta rápida
- En software Open Source
- Fácil de mantener
- Servidor local

## Retroalimentación


# Herramientas para visualización de datos

Las dashboards interactivos son herramientas de visualización que permiten a los usuarios comprender grandes cantidades de datos y así poder tomar decisiones más informadas. A través de gráficos, mapas y cuadros les permiten ver rápidamente tendencias, reconocer relaciones y descubrir valores atípicos en los datos. 

La interactividad ayuda a optimizar el uso del espacio del tablero y actualiza las visualizaciones automáticamente a medida que el usuario cambia las entradas.

Hoy en día existe una variedad de herramientas de visualización de datos, en este documento exploraremos algunas de las mejores a fin de determinar qué herramienta emplearemos para la cración del dashboard con información de SIAgroDB.


## Python

### Dash

Dash es una libreria Open Source de Plotly que nos permite realizar diferentes tipos de dashboards interactivos que hacen uso de todas las herramientas de visualización con las que cuenta Plotly en un formato HTML.  

Entre las principales ventajas con la que cuenta Dash es que es posible utilizar tanto Python como R en el fondo. Por otro lado, se puede utilizar Markdown dentro de la app para mostrarlo en el frontend. 

```python
from dash import dcc

dcc.Markdown('''
#### Dash and Markdown

Dash supports [Markdown](http://commonmark.org/help).

Markdown is a simple way to write and format text.
It includes a syntax for things like **bold text** and *italics*,
[links](http://commonmark.org/help), inline `code` snippets, lists,
quotes, and more.
''')
```

Otra ventaja significativa es la extensa [documentación](https://dash.plotly.com/) que existe como apoyo para poder desarrollar además de la variedad de ejemplos que existen y se pueden encontrar en el [Dash Gallery](https://dash.gallery/Portal/).

Un par de ejemplos relevantes para nuestros intereses son los siguientes:

[Rate of US Posion-Induced Deaths](https://dash.gallery/dash-opioid-epidemic/)

![](https://i.imgur.com/4nJl29Y.png)

[New York Oil and Gas Production Overview](https://dash.gallery/ddk-oil-and-gas-demo/)
![](https://i.imgur.com/Zks2Lnw.jpg)


[Major League Baseball History](https://dash.gallery/dash-baseball-statistics)
![](https://i.imgur.com/9qpU63K.png)



### Streamlit

Es una herramienta que nos permite realizar apps utilizando python. Al igual que Dash es un Open Source, sin embargo su documentación no es tan extensa. Cuenta con menos herramientas de personalización sin embargo, esto hace que sea un poco más sencilla de utilizar. 

La documentación se encuentra [aquí](https://docs.streamlit.io/), mientras que algunos de los ejemplos se pueden encontrar dentro de su [galeria](https://streamlit.io/gallery). Un par de ejemplos sobre Streamlit son los siguientes:

[Interactive table app](https://share.streamlit.io/streamlit/example-app-interactive-table/main)

![](https://i.imgur.com/kRpF1eo.png)

[NYC Uber Ridersharing Data](https://share.streamlit.io/streamlit/demo-uber-nyc-pickups/main)
![](https://i.imgur.com/bc1sDaH.jpg)

[Analyzing your Goodreads Reading Habits]
![](https://i.imgur.com/NQ1pUMr.png)


## R

### Shiny

Shiny es un paquete de R que permite a los usuarios crear aplicaciones web interactivas. Esta herramienta crea una aplicación web equivalente a HTML a partir del código Shiny. Con funciones R Shiny se puede integrar código HTML y CSS nativo para que la aplicación sea presentable. Shiny combina el poder computacional de R con la interactividad de la web moderna. Shiny crea aplicaciones web que se implementan en la web utilizando su servidor o los servicios de alojamiento de R Shiny.

Shiny permite al usuario renderizar (o recargar) elementos en la aplicación, lo que reduce la carga del servidor. La estructura del código juega el papel principal en la comprensión y depuración del código. Esta característica es crucial para aplicaciones brillantes con respecto a otras aplicaciones (JavaScript). 

Este paquete es particularmente bueno para la creación rápida de prototipos y bastante fácil de usar para alguien que no es programador. La disponibilidad de muchas bibliotecas de gráficos diferentes también es una gran ventaja. Una [documentación](https://shiny.rstudio.com/) accesible facilita el uso de esta paquetería.

Finalmente estas aplicaciones pueden abrirse desde el propio ordenador, una tablet o incluso el móvil.

La galería de Shiny es basta y se puede ver en esta [página](https://shiny.rstudio.com/gallery/). Entre las aplicaciones que se pueden crear están:

[Pittsburgh Trees](https://benh.shinyapps.io/pittsburgh_trees_2/)
![](https://benhay.es/img/building-shiny-dashboards_files/final_dashboard_2.png)

[Pittsburgh Non-Traffic Citations](https://benh.shinyapps.io/pittsburgh_non-traffic_citations/#section-where-are-citations-occurring)
![](https://benhay.es/img/building-shiny-dashboards_files/final_dashboard.png)

[COVID-19 tracker](https://shiny.rstudio.com/gallery/covid19-tracker.html)
![](https://wordpress.appsilon.com/wp-content/uploads/2022/03/rstudio-covid-19-tracker-life-science-dashboard.png)

[Pasture Potential Tool](https://www.dairynz.co.nz/feed/improving-pasture-performance/pasture-potential-tool/)
![](https://wordpress.appsilon.com/wp-content/uploads/2022/05/2-2.png)

### Flexdashboard

[Flexdashbaord](https://rstudio.github.io/flexdashboard/articles/flexdashboard.html) es un paquete de R que se puede instalar desde CRAN, se basa específicamente en R Markdown y admite widgets html y gráficos de cuadrícula.

Una de las principales ventajas de Flexdashboard es que es de código abierto, gratuito y de desarrollo rápido. Este paquete es muy bien soportado por RStudio. La belleza de Flexdashboard es que se basa en un estilo basado en filas y columnas, lo que facilita cambiar el diseño de la cuadrícula del tablero. 
Combinando con Tidyverse, un paquete popular en R que usa el principio de la gramática de los gráficos, los tableros son faciles y divertidos. Las estadísticas e incluso el dasboard son reproducibles, y se pueden cambiar parámetros o corregir errores sin muchos problemas, se puede representar el tablero en HTML y adjuntarlo en el correo electrónico o incrustarlo en su sitio web. También se puede publicar el tablero en Rpubs, un sitio de publicación web gratuito para R.

Sin embargo, los dashboards creados a partir de Flexdashboard son solo estáticos; es decir, se tiene menos control sobre la interfaz de usurio. Para hacerlo dinámico se pude instalar R Shiny Sin embargo, publicar los tableros puede ser un desafío.


[Sales Report with Highcharter](https://beta.rstudioconnect.com/jjallaire/htmlwidgets-highcharter/htmlwidgets-highcharter.html#sales-by-category)
![](https://i.imgur.com/j8k8F96.jpg)

[NBA Scoring (2008)](https://beta.rstudioconnect.com/jjallaire/htmlwidgets-d3heatmap/htmlwidgets-d3heatmap.html)
![](https://i.imgur.com/n6E4ZZ3.png)




### Tableau

[Tableau](https://www.tableau.com/es-mx/why-tableau/what-is-tableau) es uno de los líderes en el ámbito de la visualización de datos y la inteligencia empresarial, ayuda a los usuarios a crear rápidamente visualizaciones interactivas. El software maneja la mayor parte del trabajo preliminar detrás de escena y proporciona diseños sencillos que se pueden configurar para hacer tablas y gráficos. 

Es una herramienta fácil de aprender en comparación con otras, ya que la mayor parte del trabajo de visualización se puede completar mediante una sencilla interfaz de arrastrar y soltar. Los tableros diseñados con Tableau se pueden usar para hacer que la narración de datos sea personal y efectiva, ya que se pueden crear visualizaciones personalizadas con una codificación mínima. Incluso cuando se requiere codificación, el lenguaje es similar al de SQL, que ya utilizan muchos profesionales de datos en múltiples industrias. 
Tableau también se puede usar para visualizar datos espaciales. Reconoce el formato de archivo de forma de ESRI, así como los formatos KML y GeoJason para mostrar unidades geográficas como condados, estados o países. Los usuarios también tienen la capacidad de agregar un mapa de Mapbox a su panel de control, lo que puede hacer que la realización de análisis de ubicación sea más fácil y rápida. Las propiedades de la capa del mapa, como el terreno o la costa, se pueden filtrar o ajustar con facilidad. De manera similar, el software puede conectarse a muchas bases de datos como MySQL y Teradata y puede manejar grandes cantidades de datos de manera efectiva. Como profesional, también puede compartir y publicar sus resultados en Tableau Server o Tableau Publi
c para sus partes interesadas, lo que les facilita el acceso a sus hallazgos.

Para realizar visualizaciones en Tableau, se requiere de una licencia la cuál se debe comprar, aunque es posible crear y publicar el dashboard en Tableau Public, que es gratuito. Si bien Tableau ha evolucionado en sus capacidades para visualizar datos espaciales, todavía está rezagado con respecto a la competencia, puede visualizar y obtener información rápidamente si tiene datos en formato de latitud y longitud; sin embargo, se debe tener cuidado al realizar cualquier análisis espacial. Los procesos de análisis espacial, como el recorte espacial, tampoco están disponibles en Tableau, y tampoco es bueno para importar datos ráster, aunque se pueden realizar algunos trucos, como importar una imagen ráster como fondo e identificar sus números de fila y columna de píxeles.

[Nationwide US census engagement](https://www.tableau.com/data-insights/dashboard-showcase/explore-nationwide-us-census-engagement)
![](https://i.imgur.com/YAMKuVg.jpg)

[Towards Better Climate](https://public.tableau.com/app/profile/nontharatt.jarnyaharn/viz/TowardsBetterClimate-DeloittesEMEAIronVizGrandFinale/TowardsBetterClimate)
![](https://i.imgur.com/NDytwIK.jpg)

## Comparativa

|                       | Dash     | Streamlit | Shiny       | Flexdashboard | Tableau |
| --------------------- | -------- | --------- | ----------- | ------------- | ------- |
| Documentación         | ✔️✔️✔️   | ✔️✔️      | ✔️✔️✔️      | ✔️✔️          | ✔️✔️✔️  |
| Lenguaje              | R/Python | Python    | R           | R             | SQL     |
| *Open Source*           | ✔️       | ✔️        | ✔️          | ✔️            |  NO  |
| Tipo se servidor      | Local    | Local     | Local/Shiny | Local/Shiny   |    Tableau     |
| Mantenimiento|✔️ |✔️ |✔️ | ✔️ |✔️ 
| Visualización móviles|✔️|No óptima|✔️ |✔️ |✔️ |


