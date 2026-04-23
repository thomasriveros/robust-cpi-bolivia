################################################################################
# PROJECT: Synthetic CPI for Bolivia (Fidalga Tracker)
# AUTHOR: Thomas Riveros
# DATE: February 2026
# GOAL: Reproduce Robust Jevons-Laspeyres Index with 50% Outlier Cap
################################################################################

# 1. LOAD LIBRARIES
library(httr)
library(jsonlite)
library(tidyverse)
library(lubridate)
library(stringr)
library(scales)

# 2. SET PROJECT PATHS
# Adjust these if you move your project folder
project_dir <- "~/Desktop/Bolivia Research Project/Robust CPI/R Replication"
fixed_map_path <- file.path(project_dir, "Fixed Map.csv")
tracker_results_path <- "~/Downloads/fidalga_tracker_results.csv" # For comparison

# 3. IMPORT REFERENCE DATA (Weights & Maps)
# Official 2016-Base INE Weights
weights_fixed <- data.frame(
  Govt_Cat = c(
    "Alimentos y Bebidas No Alcohólicas", "Alimentos Consumidos Fuera del Hogar",
    "Transporte", "Vivienda y Servicios Básicos", "Bienes y Servicios Diversos",
    "Prendas de Vestir y Calzados", "Recreación y Cultura", 
    "Muebles, Bienes y Servicios Domésticos", "Comunicaciones", "Educación", 
    "Salud", "Bebidas Alcohólicas y Tabaco"
  ),
  weight = c(27.06, 13.95, 9.07, 8.56, 7.55, 7.56, 6.22, 6.08, 5.43, 4.07, 3.55, 0.88)
)

fixed_map <- read_csv(fixed_map_path, col_types = cols(id_producto = col_character()))

# 4. FETCH DATA FROM GITHUB (Fidalga Prices)
api_url <- "https://api.github.com/repos/mauforonda/precios/contents/data/fidalga/precios"
req <- GET(api_url)
stop_for_status(req)
file_list <- fromJSON(content(req, "text"))

csv_urls <- file_list %>%
  filter(str_detect(name, "\\.csv$")) %>%
  pull(download_url)

all_prices <- csv_urls %>%
  map_df(~ read_csv(.x, col_types = cols(.default = "c"))) %>%
  mutate(
    fecha_dt = as.Date(fecha),
    precio = as.numeric(precio)
  )

# 5. CALCULATE PRICE RELATIVES (Matched-Model)
Combo_DF <- left_join(fixed_map, all_prices, by = "id_producto") %>%
  select(-fecha)

Price_Relatives_Cleaned <- Combo_DF %>%
  arrange(id_producto, fecha_dt) %>%
  group_by(id_producto) %>%
  mutate(
    precio_prev = lag(precio),
    fecha_prev = lag(fecha_dt),
    days_diff = as.numeric(fecha_dt - fecha_prev),
    price_relative = ifelse(days_diff == 1, precio / precio_prev, NA),
    # Clean encoding artifacts (Mojibake) in category names
    `Govt Cat.` = `Govt Cat.` %>%
      str_replace_all("√≥", "ó") %>% str_replace_all("√©", "é") %>%
      str_replace_all("√°", "á") %>% str_replace_all("√≠", "í") %>%
      str_replace_all("√∫", "ú") %>% str_replace_all("√±", "ñ") %>%
      str_trim()
  ) %>%
  ungroup() %>%
  filter(!is.na(price_relative))

# 6. ELEMENTARY AGGREGATION (Daily Jevons)
# Applying the calibrated ±50% Outlier Cap
Category_Jevons_Daily <- Price_Relatives_Cleaned %>%
  filter(!is.infinite(price_relative), 
         price_relative >= 0.5, price_relative <= 1.5) %>%
  group_by(fecha_dt, `Govt Cat.`) %>%
  summarize(
    daily_relative = exp(mean(log(price_relative))),
    n_products = n(),
    .groups = "drop"
  )

# 7. ROBUST CATEGORY FILTERING (n >= 10)
robust_categories <- Category_Jevons_Daily %>%
  group_by(`Govt Cat.`) %>%
  summarize(avg_n = mean(n_products)) %>%
  filter(avg_n >= 10) %>%
  pull(`Govt Cat.`)

# 8. CHAINING & TOTAL CPI CALCULATION (Laspeyres)
cpi_final_robust <- Category_Jevons_Daily %>%
  filter(`Govt Cat.` %in% robust_categories) %>%
  arrange(`Govt Cat.`, fecha_dt) %>%
  group_by(`Govt Cat.`) %>%
  mutate(
    # Set anchor (1.0) for the first observation of each category
    daily_relative = ifelse(row_number() == 1, 1, daily_relative),
    index_level = 100 * cumprod(daily_relative)
  ) %>%
  left_join(weights_fixed, by = c("Govt Cat." = "Govt_Cat")) %>%
  group_by(fecha_dt) %>%
  mutate(norm_weight = weight / sum(weight, na.rm = TRUE)) %>%
  summarize(
    total_synthetic_cpi = sum(index_level * norm_weight, na.rm = TRUE),
    robust_categories_included = n()
  )

# 9. FINAL PLOT: TOTAL SYNTHETIC CPI
ggplot(cpi_final_robust, aes(x = fecha_dt, y = total_synthetic_cpi)) +
  geom_line(color = "steelblue", size = 1.2) +
  geom_hline(yintercept = 100, linetype = "dashed") +
  theme_minimal() +
  labs(
    title = "Total Synthetic CPI: Bolivia (Robust Sample)",
    subtitle = "±50% Outlier Cap | Weighted Jevons-Laspeyres Index",
    y = "Index Value (Base 100)", x = "Date"
  )

# 10. CLEAN UP & SAVE RESULTS
rm(all_prices, Combo_DF, Price_Relatives_Cleaned, req, file_list)
gc()

save(cpi_final_robust, Category_Jevons_Daily, weights_fixed, 
     file = file.path(project_dir, "Final_CPI_Workspace.RData"))

message("Replication Complete. Workspace saved to: ", project_dir)