library(velox)
library(purrr)
library(ncdf4)
library(raster)
library(stringr)
library(tidyr)


# get all the projections raster file names
files <- list.files("D:/victoria_projections/projections/", full.names = TRUE)
file_names <- list.files("D:/victoria_projections/projections/", full.names = FALSE)
file_names <- gsub(".tif", "", file_names)
file_names<- gsub("remind-magpie", "remind_magpie", file_names)

# read in one of the future projections files to get the crs and extent information
proj_ras <- raster(files[47])

# read in the raster holding the cell areas
cell_area <- raster("C:/data/luh2_v2/staticData_quarterdeg.nc", 
                    varname = "carea")

# make sure the crs matches the projections
crs(cell_area) <- crs(proj_ras)

# crop the cell areas maps so that the extent matches the projections
cell_area_m <- crop(cell_area, proj_ras) %>%
  mask(proj_ras)

# it looks like the maps don't always have the same extents...
map_extents <- map_dfr(.x = files, 
                       function(x){
                         
                         ex <- x %>%
                           raster() %>%
                           extent() %>%
                           as.vector()
                         
                         i <- gsub("D:/victoria_projections/projections/", "", x)
                         i <- gsub(".tif", "", i)
                         
                         res <- data.frame(xmin = ex[1],
                                           xmax = ex[2],
                                           ymin = ex[3],
                                           ymax = ex[4],
                                           Scenario = i)
                         
                       })

map_extents %>% 
  filter(xmin != -180)
map_extents %>% 
  filter(xmax != 180)
map_extents %>% 
  filter(ymax != 83.75)

# It's in the ymin where we have some deviation...
map_extents %>% 
  filter(ymin != -56.00)

# The historical maps are slightly larger (the ymin goes down to -58, while the future projections go down to -56)
# so let's make sure they're all cut to the same amount

# set up the empty data frame to hold the results
means <- data.frame(WeightedMean = rep(NA, length(files)),
                    files = file_names)

for(i in 1:length(files)){
  
  print(paste("working on file", i, "of", length(files)))
  
  # read in the raster
  ras <- raster(files[i])
  
  # if you're working with the historical projections, then you need to first make sure that the extent of the projections matches the cell area maps
  if(grepl("historical", files[i])){
    
    print("cropping the map for the following file")
    print(files[i])
    
    # crop the cell areas maps so that the extent matches the projections
    ras <- crop(ras, proj_ras) %>%
      mask(proj_ras)
    
  }
  
  means$WeightedMean[i] <- ras %>%
    
    # get the values
    getValues() %>%
    
    # calculate the weighted mean
    weighted.mean(w = getValues(cell_area_m),
                  na.rm = TRUE)
  
}

# separate out the columns to give the biodiversity metric, the land-use/climate scenario and the year
means <- means %>% 
  separate(col = files,
           into = c("metric", "scenario", "year"),
           sep = "-",
           remove = FALSE)

write.csv(means, "D:/victoria_projections/globalMeans.csv", row.names = FALSE)


plot(WeightedMean ~ year, data = means, type = "l")
