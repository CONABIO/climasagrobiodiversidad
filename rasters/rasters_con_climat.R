##librerias
library(raster)
library(sp)
library(rgdal)
library(sf)
library(dplyr)
library(tidyverse)
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
maices <- maices |> select(-taxon, -proyecto)

#sistema de coordenadas
dec<-"+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
xcoors<-st_as_sf(maices,coords = c("sitio.longitud", "sitio.latitud"), crs = dec)

#extracción de valores del raster de bioclimas
coors_bioclimas <- extract(bioclimas,xcoors)

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
  mutate(Precip_prom_may_oct = rowMeans2(as.matrix(maices_cond_clim_df[,c(35,36,37,38,39,40)])))


################ rasters Temperatura mínima ###########
#######################################################

#lectura de bandas del raster
temperatura <- stack(list.files(path="./tmi198009gw", pattern=".tif$", full.names=T))

#extracción de valores del raster de temp mínima
coors_temperatura <- extract(temperatura,xcoors)

#incorporación de valores del raster a la base de maíces
maices_cond_clim_df <-cbind(maices_cond_clim_df, coors_temperatura)


################ rasters Temperatura máxima ###########
#######################################################

#lectura de bandas del raster
temperatura_max <- stack(list.files(path="./tm198009gw", pattern=".tif$", full.names=T))

#extracción de valores del raster de temp mínima
coors_temperatura_max <- extract(temperatura_max,xcoors)

#incorporación de valores del raster a la base de maíces
maices_cond_clim_df <-cbind(maices_cond_clim_df, coors_temperatura_max)

#creación de la variable de temp max promedio may-oct 2000
maices_cond_clim_df <- maices_cond_clim_df |> 
  #replace(is.na(), 0) %>% 
  mutate(temp_max_prom_may_oct = rowMeans2(as.matrix(maices_cond_clim_df[,c(60,61,62,63,64,65)])))



############################################################
#################  Base CONDICONES SITIO  #################
###########################################################

#selección de variables para la base CONDICIONES SITIO
df_cond_sitio <- maices_cond_clim_df |> 
                    select(id,Precip_prom_may_oct,temp_max_prom_may_oct)

#convertir en formato largo el dataframe 'df_cond_sitio', para crear las variables 'condicion'
#y 'valor' del modelo de datos'condiones-sitio'
df_cond_sitio <- df_cond_sitio |> 
                  pivot_longer(cols = c("Precip_prom_may_oct","temp_max_prom_may_oct"),
                               names_to = "condicion",
                               values_to = "valor")

#Recodificación de la variable 'condicion'
df_cond_sitio$condicion[df_cond_sitio$condicion=="Precip_prom_may_oct"] <- "Precipitación media para los meses mayo-octubre periodo 2000"
df_cond_sitio$condicion[df_cond_sitio$condicion=="temp_max_prom_may_oct"] <- "Temperatura máxima media para los meses mayo-octubre periodo 2000"

#creación de las variables 'unidad', 'fuente' y 'sitio_id' del modelo de datos 'condiciones-sitio'
df_cond_sitio <- df_cond_sitio |> 
                    mutate(unidad=ifelse(condicion=="Temperatura máxima media para los meses mayo-octubre periodo 2000",
                                     "°C", "mm"),
                           nombre_corto=ifelse(condicion=="Temperatura máxima media para los meses mayo-octubre periodo 2000",
                                               "Tmax_mean_mayoct_2000", "Pptmean_mayoct_2000"),
                           fuente=ifelse(condicion=="Temperatura máxima media para los meses mayo-octubre periodo 2000",
                                         "Se calculó el promedio mensual para los meses mayo-octubre a partir de extraer el valor de la celda donde cae el punto del sitio en los rasters mensuales de Cuervo-Robayo A.P., C. Ureta, M.A. Gómez-Albores, A.K. Meneses-Mosquera, O. Téllez-Valdés, E. Martínez-Meyer, (27/08/2019). 'Temperatura máxima mensual, periodo: 2000 (1980-2009)', edición: 1. Instituto de Biología, Universidad Nacional Autónoma de México. Estos mapas forman parte de la publicación: Cuervo-Robayo, A. P., Ureta, C., Gómez-Albores, M. A., Meneses-Mosquera, A. K., Téllez-Valdés, O., y E. Martínez-Meyer. (2020). One hundred years of climate change in Mexico. Plos One. https://doi.org/10.1371/journal.pone.0209808. Ciudad de México, México.",
                                         "Se calculó el promedio mensual para los meses mayo-octubre a partir de extraer el valor de la celda donde cae el punto del sitio en los rasters mensuales de Cuervo-Robayo A.P., C. Ureta, M.A. Gómez-Albores, A.K. Meneses-Mosquera, O. Téllez-Valdés, E. Martínez-Meyer, (27/08/2019). 'Precipitación mensual, periodo: 2000 (1980-2009)', edición: 1. Instituto de Biología, Universidad Nacional Autónoma de México. Estos mapas forman parte de la publicación: Cuervo-Robayo, A. P., Ureta, C., Gómez-Albores, M. A., Meneses-Mosquera, A. K., Téllez-Valdés, O., y E. Martínez-Meyer. (2020). One hundred years of climate change in Mexico. Plos One. https://doi.org/10.1371/journal.pone.0209808. Ciudad de México, México.")) |> 
                    rename("sitio_id"=id)  


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






