##librerias
library(tidyverse)
library(tidyr)
library(raster)
library(sp)
library(rgdal)
library(sf)
library(dplyr)
library(matrixStats)
library(jsonlite)


################ raster Bioclimas ###########
##############################################

#set working directory
setwd("~/rasters")

#lectura de bandas del raster
bioclimas <- stack(list.files(path="./b19802009gw", pattern=".tif$", full.names=T))
#plot(bioclimas)

#Lectura de BD de maíces
maices <- read.csv("./maices.csv")
maices <- maices |> dplyr::select(-taxon, -proyecto)

#sistema de coordenadas
dec<-"+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
xcoors<-st_as_sf(maices,coords = c("sitio.longitud", "sitio.latitud"), crs = dec)

#extracción de valores del raster de bioclimas
coors_bioclimas <- raster::extract(bioclimas,xcoors)

#incorporación de valores del raster a la base de maíces
maices_cond_clim_df<-cbind(maices, coors_bioclimas)


################ rasters Precipitación ###########
##################################################

#lectura de bandas del raster
precipitacion <-stack(list.files(path="./p19802009gw", pattern=".tif$", full.names=T))

#extracción de valores del raster de precipitación
coors_precipitacion <-extract(precipitacion,xcoors)

#incorporación de valores del raster a la base de maíces
maices_cond_clim_df <-cbind(maices_cond_clim_df, coors_precipitacion)

# creación de la variable de precipitación promedio may-oct 2000
maices_cond_clim_df <- maices_cond_clim_df |> 
  #replace(is.na(), 0) %>% 
  mutate(Precip_invernal = rowSums2(as.matrix(maices_cond_clim_df[,c(31,32,40,41,42)])))



############################################################
#################  Base CONDICONES SITIO  #################
###########################################################

#selección de variables para la base CONDICIONES SITIO
df_cond_sitio <- maices_cond_clim_df |> 
                    dplyr::select(id,bio01_t3gw,bio12_t3gw, Precip_invernal)

#convertir en formato largo el dataframe 'df_cond_sitio', para crear las variables 'condicion'
#y 'valor' del modelo de datos'condiones-sitio'
df_cond_sitio <- df_cond_sitio |> 
                  pivot_longer(cols = c("bio01_t3gw","bio12_t3gw", "Precip_invernal"),
                               names_to = "nombre corto",
                               values_to = "valor")

#creación de las variables 'unidad', 'fuente' y 'sitio_id' del modelo de datos 'condiciones-sitio'
df_cond_sitio <- df_cond_sitio |> 
                    mutate(unidad=ifelse(`nombre corto`=="bio01_t3gw", "°C", "mm"),
                           condicion=ifelse(`nombre corto`=="bio01_t3gw",
                                               "Temperatura media anual periodo 2000", "Precipitación anual perido 2000"),
                           fuente="Valor extraído de la celda donde cae el punto del sitio en los rasters de Cuervo-Robayo A.P., C. Ureta, M.A. Gómez-Albores, A.K. Meneses-Mosquera, O. Téllez-Valdés, E. Martínez-Meyer, (27/08/2019). 'Bioclimas, periodo: 2000 (1980-2009)', edición: 1. Instituto de Biología, Universidad Nacional Autónoma de México. Estos mapas forman parte de la publicación: Cuervo-Robayo, A. P., Ureta, C., Gómez-Albores, M. A., Meneses-Mosquera, A. K., Téllez-Valdés, O., y E. Martínez-Meyer. (2020). One hundred years of climate change in Mexico. Plos One. https://doi.org/10.1371/journal.pone.0209808 Ciudad de México, México.") |> 
                    rename("sitio_id"=id) |> 
                    rename("nombre_corto"=`nombre corto`)

df_cond_sitio <- df_cond_sitio |> 
                    select(sitio_id,condicion,valor,unidad,nombre_corto,fuente)

############################################################
###############  Conversión a formato JSON  ###############
###########################################################

#conversión a formato JSON el dataframe 'df_conf_sitio', de acuerdo con el modelo
# 'condiciones-sitio'
cond_sit_json <- toJSON(df_cond_sitio, dataframe = 'rows', pretty = T)

#conversión del formato json a un objeto de R para poder exportarlo
cond_sit_tabla <- fromJSON(cond_sit_json)

#exportar la base 'cond_sit_json' para ser cargada en la spa de maices-siagro
write.csv(cond_sit_tabla,"cond_sit_json.csv")






