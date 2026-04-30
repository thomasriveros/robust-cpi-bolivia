# ==============================================================================
# PROJECT: Robust Synthetic CPI (Bolivia Supermarket Data)
# MASTER SCRIPT: DATA INGESTION, CALCULATION, AND VALIDATION
# ==============================================================================

# Load required libraries
library(dplyr)
library(readr)
library(purrr)
library(stringr)
library(tidyr)     # Required for expand_grid
library(lubridate)
library(ggplot2)
library(glue)

# ---------------------------------------------------------
# PART 1: DATA INGESTION FROM GITHUB
# ---------------------------------------------------------
cities <- c("cochabamba", "santa_cruz", "la_paz")

# Generate a sequence of months from July 2024 to April 2026
months <- format(seq(as.Date("2024-07-01"), as.Date("2026-04-01"), by = "month"), "%Y_%m")
base_url <- "https://raw.githubusercontent.com/mauforonda/precios/master/data/hipermaxi"

# Function to safely fetch monthly data
fetch_monthly_data <- function(city, month_str) {
  url <- glue::glue("{base_url}/{city}/{month_str}.csv")
  tryCatch({
    df <- read_csv(url, show_col_types = FALSE)
    if (nrow(df) > 0) df <- df %>% mutate(city = city)
    return(df)
  }, error = function(e) return(tibble()))
}

cat("Downloading historical price data...\n")
raw_prices <- expand_grid(city = cities, month_str = months) %>%
  pmap_dfr(~ fetch_monthly_data(..1, ..2))

cat("Downloading product catalog and local AI categories...\n")
productos_url <- "https://raw.githubusercontent.com/mauforonda/precios/master/data/hipermaxi/productos.csv"

# Column names confirmed: id_producto, producto, categoria, subcategoria
productos_cat <- read_csv(productos_url, show_col_types = FALSE)

# Ensure this file exists in your local working directory
# It uses 'Product ID' which we rename to match the master key
ai_mapped_cats <- read_csv("Final_Complete_Categories (1).csv", show_col_types = FALSE) %>%
  rename(id_producto = `Product ID`)

# Initial Master Merge
cpi_data_mapped <- raw_prices %>%
  left_join(productos_cat, by = "id_producto") %>%
  left_join(ai_mapped_cats %>% select(id_producto, Category, Confidence, Flag), by = "id_producto")

# ---------------------------------------------------------
# PART 1.5: CALCULATE DAILY RELATIVES (relative_dod)
# ---------------------------------------------------------
cat("Calculating day-to-day price relatives (relative_dod)...\n")
cpi_data_mapped <- cpi_data_mapped %>%
  mutate(fecha = as.Date(fecha)) %>%
  group_by(city, id_producto) %>%
  arrange(fecha) %>%
  mutate(
    precio_prev = lag(precio),
    relative_dod = precio / precio_prev
  ) %>%
  ungroup()

# ---------------------------------------------------------
# PART 2: DEFINE CORE BASKET & CITY WEIGHTS
# ---------------------------------------------------------
cat("Defining core basket and regional weights...\n")

core_basket <- data.frame(
  Category = c("Alimentos y Bebidas No Alcohólicas",
               "Bienes y Servicios Diversos",
               "Muebles, Bienes y Servicios Domésticos",
               "Bebidas Alcohólicas y Tabaco",
               "Prendas de Vestir y Calzados"),
  Raw_Weight = c(27.06, 7.55, 6.08, 0.88, 7.56)
) %>%
  mutate(Normalized_Weight = Raw_Weight / sum(Raw_Weight))

city_weights <- data.frame(
  City = c("santa_cruz", "la_paz", "cochabamba"),
  Raw_Weight = c(34.2535, 32.2927, 16.0492)
) %>%
  mutate(Weight = Raw_Weight / sum(Raw_Weight))

# ---------------------------------------------------------
# PART 3: INDEX CALCULATION (FILTERING AND CHAINING)
# ---------------------------------------------------------
cat("Calculating chained indexes...\n")

# 1. Identify and exclude "Temporada" (Seasonal) products using the subcategoria column
temporada_ids <- cpi_data_mapped %>%
  filter(grepl("Temporada", subcategoria, ignore.case = TRUE)) %>%
  pull(id_producto) %>% 
  unique()

# 2. Filter to core categories and valid price relatives
clean_core_data <- cpi_data_mapped %>%
  filter(!id_producto %in% temporada_ids) %>%
  filter(Category %in% core_basket$Category) %>%
  filter(relative_dod > 0, !is.na(relative_dod))

# 3. Daily Jevons index calculation
chained_elementary <- clean_core_data %>%
  group_by(city, Category, fecha) %>%
  summarise(daily_jevons = exp(mean(log(relative_dod), na.rm = TRUE)), .groups = "drop") %>%
  arrange(city, Category, fecha) %>%
  group_by(city, Category) %>%
  mutate(chained_index = 100 * cumprod(daily_jevons)) %>%
  ungroup()

# 4. Aggregate to City Level
city_level_cpi <- chained_elementary %>%
  left_join(core_basket, by = "Category") %>%
  group_by(city, fecha) %>%
  summarise(city_index = sum(chained_index * Normalized_Weight, na.rm = TRUE) /
              sum(Normalized_Weight, na.rm = TRUE), .groups = "drop")

# 5. Aggregate to National Level
national_cpi <- city_level_cpi %>%
  mutate(join_key = tolower(gsub(" ", "_", city))) %>%
  left_join(city_weights %>% mutate(join_key = tolower(gsub(" ", "_", City))), by = "join_key") %>%
  group_by(fecha) %>%
  summarise(national_index = sum(city_index * Weight, na.rm = TRUE) /
              sum(Weight, na.rm = TRUE), .groups = "drop")

cat("National CPI calculation finished successfully.\n")