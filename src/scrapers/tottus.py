import time
import pandas as pd
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils.driver_config import get_driver

def scrapear_tottus(url, categoria, output_folder="data/raw"):
    print(f"--- Iniciando Scraping Tottus: {categoria} ---")
    driver = get_driver(headless=False)
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    
    scraped_data = []
    os.makedirs(output_folder, exist_ok=True)

    page_count = 1
    
    try:
        while True:
            # Esperar carga inicial
            try:
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[pod-layout]")))
            except:
                print("No se detectaron productos o la página tardó demasiado.")
                break

            # Scroll para Lazy Loading
            last_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(2):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height: break
                last_height = new_height

            # Extraer data
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            cards = soup.find_all('div', attrs={'pod-layout': True})
            
            for card in cards:
                try:
                    # Nombre compuesto (Marca + Nombre)
                    brand = card.find('b', class_=lambda x: x and 'pod-title' in x)
                    name = card.find('b', class_=lambda x: x and 'pod-subTitle' in x)
                    brand_txt = brand.text.strip() if brand else ""
                    name_txt = name.text.strip() if name else "Desconocido"
                    full_name = f"{brand_txt} {name_txt}".strip()

                    # Lógica de precios (Buscamos el menor disponible)
                    prices = []
                    price_elements = card.select('div[id^="testId-pod-prices-"] li')
                    for li in price_elements:
                        if li.get('data-normal-price'): prices.append(float(li['data-normal-price']))
                        if li.get('data-internet-price'): prices.append(float(li['data-internet-price']))
                        if li.get('data-cmr-price'): prices.append(float(li['data-cmr-price']))
                    
                    final_price = min(prices) if prices else 0.0

                    if full_name != "Desconocido" and final_price > 0:
                        scraped_data.append({'Producto': full_name, 'Precio': final_price})
                except:
                    continue

            # Paginación
            try:
                next_btn = driver.find_element(By.ID, "testId-pagination-bottom-arrow-right")
                if not next_btn.is_enabled(): break
                driver.execute_script("arguments[0].click();", next_btn)
                page_count += 1
                time.sleep(4)
                print(f"  -> Página {page_count} procesada...")
            except:
                break

    except Exception as e:
        print(f"Error en Tottus {categoria}: {e}")
    finally:
        driver.quit()

    # Guardar CSV
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        filename = f"{output_folder}/tottus_{categoria.lower().replace(' ', '_')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
        print(f"Guardado: {filename} ({len(df)} productos)\n")
    else:
        print(f"No data para {categoria}\n")