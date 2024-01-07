# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 19:02:26 2023

@author: juani
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pandas as pd
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

options = webdriver.ChromeOptions()
options.headless = False
driver = webdriver.Chrome(service=Service(),options=options)
wait = WebDriverWait(driver, 10)
url = 'https://offcampus.uwo.ca/listings/'
driver.get(url)
all_data = []

current_page = 0

while True:
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.rental-listing')))
    
    listings = driver.find_elements(By.CSS_SELECTOR, 'div.rental-listing')

    for listing in listings:
        try:
            # Imagen del listado
            link_element = listing.find_element(By.CSS_SELECTOR, ".rental-listing-details h2 strong a")
            link = link_element.get_attribute('href')  # Extraer el enlace

            # Dirección
            address_element = listing.find_element(By.CSS_SELECTOR, '.rental-listing-details h2 strong a')
            address = address_element.text

            # Precio por habitación
            price_element = listing.find_element(By.CSS_SELECTOR, '.rental-listing-details h3 strong')
            price = price_element.text

            # Disponibilidad de habitaciones
            Bedrooms_element = listing.find_element(By.CSS_SELECTOR, '.rental-listing-details h3')
            Bedrooms = Bedrooms_element.text.split(",")[1].strip()

            # Fecha de disponibilidad
            date_element = listing.find_element(By.CSS_SELECTOR, '.rental-listing-details h4')
            date_available = date_element.text

            # Descripción detallada
            description_element = listing.find_element(By.CSS_SELECTOR, '.rental-listing-details p')
            description = description_element.text

            all_data.append([address, Bedrooms, price, date_available, description, link])
        except Exception as e:
            print(f"Error al procesar un listado: {e}")
            continue
    
    # Intentar hacer clic en el botón de "Next". Si no está presente o no es clickeable, salir del loop.
    try:
        current_page += 1
        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'span[onclick="GoToPage({current_page})"]')))
        next_button.click()
        sleep(5)  # Esperar 5 segundos antes de continuar
    except:
        break

driver.quit()

# Convertir los datos a un DataFrame
df = pd.DataFrame(all_data, columns=['Address', 'Bedrooms', 'Price', 'Date Available', 'Description', 'Image URL'])
df['Price'] = df['Price'].str.replace(r'[^\d.]', '', regex=True)
df['Price'] = df['Price'].astype(int)
df['Bedrooms'] = df['Bedrooms'].str.replace(r'[^\d.]', '', regex=True)
df['Bedrooms'] = df['Bedrooms'].astype(int)
df.dropna(how='all', inplace=True)
print(df)
df.to_excel('listings.xlsx')


# Graphs
plt.figure(figsize=(10, 6))
sns.histplot(df['Price'], kde=True)
plt.axvline(df['Price'].mean(), color='r', linestyle='-', label='Mean')
plt.axvline(df['Price'].median(), color='g', linestyle='-', label='Median')
plt.title('Price Distribution')
plt.legend()
plt.savefig('dist_precios.png')

# Gráfico para la distribución de habitaciones
plt.figure(figsize=(10, 6))
sns.countplot(x='Bedrooms', data=df)
plt.title('Bedroom Distribution')
plt.savefig('dist_habitaciones.png')
df = df[df['Bedrooms'] != 0]

precio_por_habitacion = df.groupby('Bedrooms')['Price'].agg(['mean', 'median']).reset_index()
precio_por_habitacion['Bedrooms'] = precio_por_habitacion['Bedrooms'].astype(int)

plt.figure(figsize=(10, 8))
ax = sns.heatmap(precio_por_habitacion.set_index('Bedrooms'), cmap='coolwarm', annot=True, fmt=".0f", annot_kws={'size': 10})
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
plt.title('Price Heatmap per Number of Bedrooms')
plt.savefig('heatmap_precios..png')

