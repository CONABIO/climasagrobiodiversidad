# Aplicación Web de datos del Proyecto Global de Maíces Nativos de la CONABIO

El proyecto Agrobiodiversidad Mexicana, tiene como objetivo construir y fortalecer mecanismos que ayuden a conservar la agrobiodiversidad mexicana y los agroecosistemas tradicionales. Dentro de sus componentes está la consolidación del Sistema de Información sobre Agrobiodiversidad (SIAgroBD), el cual integra información sobre agrobiodiversidad. Como parte de la apertura de los datos del SIAgroBD a públicos diversos, teníamos la necesidad de realizar un mapa interactivo que mostrara datos acerca de características ambientales (precipitación, temperatura) de datos del SIAgroBD, particularmente de datos del Proyecto Global de Maíces Nativos de la CONABIO. Durante la estancia de estudiantes de la maestría de ciencia de datos del ITAM en Conabio, se desarrolló una aplicación web que cumplió a cabalidad con dichos requisitos.


Para el desarrollo de la aplicación, primero se realizó un taller con personas expertas en datos de maíz y trabajo con familias campesinas, donde se definieron las historias de usos y funcionalidades deseadas de la aplicación web. Con base en estos requisitos, se hizo una lista de requerimientos técnicos y una revisión de herramientas para cumplirlos. Se optó por utilizar Dash, una libreria Open Source de Plotly que nos permite realizar diferentes tipos de dashboards interactivos que hacen uso de todas las herramientas de visualización con las que cuenta Plotly en un formato HTML. El desarrollo de la aplicación se realizó utilizando una combinación de scripts de python y R, que se alimentan dinámicamente de los datos del SIAgroBD por medio de consultas GraphQL.


La información de las variables bioclimáticas, temperatura media anual y precipitación anual, se obtuvo a partir de extraer el valor de la celda donde cae el punto del sitio de colecta en los rasters mensuales que se encuentran publicados en el portal de Geoinformación 2022 de la CONABIO.


La estructura del repositorio es la siguiente

```
.
├── assets                        # Carpeta con JS para la aplicación
├── dash                          # Entorno virtual
├── rasters                     
│   ├── .keep                   
│   ├── query_maices.py         
│   ├── rasters_con_climat.R      # Script para extraer información de los rasters
├── LICENCE                                  
├── README.md
├── altitud.png                   # Imagen para rainplot                   
├── get-pip.py                                  
├── precipitacion.png             # Imagen para rainplot
├── query.py                      # Script para extraer datos del SIAgro
├── requirements.txt              # Archivo con las paqueterias necesarias para utilizar la aplicación            
├── temperatura.png               # Imagen para rainplot                                
├── test.py                       # Script de la aplicación
└── ...
```

Para la ejecución del código que se encuentra en este repositorio se recomienda activar primero el entorno virtual ```dash``` a través de la linea de comando e instalar todas paqueterías necesarias que se encuentran en ```requirements.txt``` utilizando el siguiente comando.

```{python}
pip3 install -r requirements.txt
```

# Servidor

Se modificó el script principal para que los datos no tardaran en cargarse y además se mostraran todos los ejemplares de un taxón (ver https://github.com/CONABIO/climasagrobiodiversidad/issues/1). 

Dado que se crea un csv plano para obtener la información, el csv se genera diario a las 23:45 horas. El script que se ejecuta se puede consultar en el servidor con el comando `crontab -l` para obtener la ubicación del mismo. 
