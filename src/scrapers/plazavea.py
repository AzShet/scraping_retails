import time
import pandas as pd
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils.driver_config import get_driver

def scrapear_plazavea(url, categoria, output_folder="data/raw"):
    print(f"--- Iniciando Scraping Plaza Vea: {categoria} ---")
    driver = get_driver(headless=False) # Pon True si no quieres ver la ventana
    driver.get(url)

    productos = []
    precios = []
    
    # Asegurar que la carpeta exista
    os.makedirs(output_folder, exist_ok=True)

    try:
        while True:
            # Espera dinámica
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "showcase-grid"))
            )
            time.sleep(2) # Pausa de seguridad

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            items = soup.find_all('div', class_='ga-product-item')

            if not items:
                break

            for item in items:
                nombre = item.get('data-ga-name')
                precio = item.get('data-ga-price')
                
                if nombre:
                    productos.append(nombre)
                    # Convertir precio a float seguro
                    try:
                        precios.append(float(precio) if precio else 0.0)
                    except:
                        precios.append(0.0)

            # Paginación
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".pagination__item.page-control.next:not(.disabled)")
                driver.execute_script("arguments[0].click();", next_button)
                print(f"  -> Avanzando página...")
            except:
                print("  -> Fin de la paginación.")
                break

    except Exception as e:
        print(f"Error durante el scraping de {categoria}: {e}")
    finally:
        driver.quit()

    # Guardar CSV Estandarizado
    if productos:
        df = pd.DataFrame({'Producto': productos, 'Precio': precios})
        filename = f"{output_folder}/pv_{categoria.lower().replace(' ', '_')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
        print(f"Guardado: {filename} ({len(df)} productos)\n")
    else:
        print(f"No se encontraron productos para {categoria}\n")