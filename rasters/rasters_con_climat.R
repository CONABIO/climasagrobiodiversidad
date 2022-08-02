##librerias
library(raster)
library(sp)
library(rgdal)
library(sf)
library(dplyr)
library(matrixStats)



################ raster Bioclimas ###########
##############################################

#lectura de bandas del raster
bioclimas <- stack(list.files(path="./b19802009gw", pattern=".tif$", full.names=T))
#plot(bioclimas)

#Lectura de BD de maíces
maices <- read.csv("./maices.csv")

#sistema de coordenadas
dec<-"+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
xcoors<-st_as_sf(maices,coords = c("longitud", "latitud"), crs = dec)

#extracción de valores del raster de bioclimas
coors_bioclimas <- extract(bioclimas,xcoors)

#incorporación de valores del raster a la base de maíces
maices_cond_clim_df<-cbind(maices, coors_bioclimas)

maices_cond_clim_df <-maices_cond_clim_df |> 
  rename("temp_media_anual"= bio01_t3gw,
         "rango_temp_diurna"= bio02_t3gw,
         "Isotermalidad" = bio03_t3gw,
         "Estacionalidad_temp" = bio04_t3gw,
         "Temp_maxima" = bio05_t3gw,
         "Temp_minima" = bio06_t3gw,
         "Rango_anual_temp" = bio07_t3gw,
         "Temp_media_trim_+lluvioso" = bio08_t3gw,
         "Temp_media_trim_+seco" = bio09_t3gw,
         "Temp_media_trim_+calido" =  bio10_t3gw,         
         "Temp_media_trim_+frio" = bio11_t3gw,
         "Precipitación_anual"= bio12_t3gw,        
         "Precip_mes_+lluvioso" = bio13_t3gw,        
         "Precip_mes_+seco" = bio14_t3gw,        
         "Estacionalidad_precip" = bio15_t3gw,        
         "Precipt_trim_+lluvioso" = bio16_t3gw,       
         "Precipt_trim_+seco" = bio17_t3gw,         
         "Precipt_trim_+calido" = bio18_t3gw,         
         "Precipt_trim_+frio" = bio19_t3gw )



################ rasters Precipitación ###########
##################################################

#lectura de bandas del raster
precipitacion <-stack(list.files(path="./p19802009gw", pattern=".tif$", full.names=T))

#plot(precipitacion)

#extracción de valores del raster de precipitación
coors_precipitacion <-extract(precipitacion,xcoors)

#incorporación de valores del raster a la base de maíces
maices_cond_clim_df <-cbind(maices_cond_clim_df, coors_precipitacion)
maices_cond_clim_df <- maices_cond_clim_df |> rename("Precip_ene00" = ppt01_t3gw,
                              "Precip_feb00" = ppt02_t3gw,
                              "Precip_mar00" = ppt03_t3gw,
                              "Precip_abr00" = ppt04_t3gw,
                              "Precip_may00" = ppt05_t3gw,
                              "Precip_jun00" = ppt06_t3gw,
                              "Precip_jul00" = ppt07_t3gw,
                              "Precip_ago00" = ppt08_t3gw,
                              "Precip_sep00" = ppt09_t3gw,
                              "Precip_oct00" = ppt10_t3gw,
                              "Precip_nov00" = ppt11_t3gw,
                              "Precip_dic00" = ppt12_t3gw)


# creación de variables de precipitación máxima y mínima
maices_cond_clim_df <- maices_cond_clim_df |> 
  #replace(is.na(), 0) %>% 
  mutate(Precip_max = rowMaxs(as.matrix(maices_cond_clim_df[,c(42,43,44,45,46,47,48,49,50,51,52,53)])),
         Precip_min = rowMins(as.matrix(maices_cond_clim_df[,c(42,43,44,45,46,47,48,49,50,51,52,53)])))
  


################ rasters Temperatura mínima ###########
#######################################################

#lectura de bandas del raster
temperatura <- stack(list.files(path="./tmi198009gw", pattern=".tif$", full.names=T))

#plot(precipitacion)


#extracción de valores del raster de temp mínima
coors_temperatura <- extract(temperatura,xcoors)

#incorporación de valores del raster a la base de maíces
maices_cond_clim_df <-cbind(maices_cond_clim_df, coors_temperatura)
maices_cond_clim_df <- maices_cond_clim_df |> rename("tmin_ene00" = tmin01_t3gw,
                                                     "tmin_feb00" = tmin02_t3gw,
                                                     "tmin_mar00" = tmin03_t3gw,
                                                     "tmin_abr00" = tmin04_t3gw,
                                                     "tmin_may00" = tmin05_t3gw,
                                                     "tmin_jun00" = tmin06_t3gw,
                                                     "tmin_jul00" = tmin07_t3gw,
                                                     "tmin_ago00" = tmin08_t3gw,
                                                     "tmin_sep00" = tmin09_t3gw,
                                                     "tmin_oct00" = tmin10_t3gw,
                                                     "tmin_nov00" = tmin11_t3gw,
                                                     "tmin_dic00" = tmin12_t3gw)
