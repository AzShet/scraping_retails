import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- Configuración de Selenium (sin cambios) ---
options = webdriver.ChromeOptions()
# Descomenta la siguiente línea para que el navegador no se abra visualmente
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# --- CAMBIO 1: Nueva URL de la categoría "Papel Higiénico" ---
url = "https://tottus.falabella.com.pe/tottus-pe/category/CATG14245/Papel-Higienico"

print("Accediendo a la página inicial...")
driver.get(url)

wait = WebDriverWait(driver, 20)
scraped_data = []
page_count = 1

# --- Bucle principal para recorrer todas las páginas (lógica sin cambios) ---
while True:
    print(f"\n--- Procesando Página N° {page_count} ---")
    try:
        print("Esperando a que carguen los productos...")
        # Espera a que la primera tarjeta de producto sea visible
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[pod-layout]")))
        print("¡Contenido cargado!")

        # Hacemos scroll para cargar productos adicionales (lazy loading)
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(3): # Aumentamos a 3 scrolls para mayor seguridad
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3) # Esperamos que carguen
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # --- Extracción y análisis del HTML de la página actual ---
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # El selector para las tarjetas de producto sigue siendo el mismo
        product_cards = soup.find_all('div', attrs={'pod-layout': True})
        print(f"Se encontraron {len(product_cards)} productos en esta página.")

        if not product_cards:
            print("No se encontraron más productos. Terminando.")
            break

        for card in product_cards:
            # La lógica para obtener marca y nombre no necesita cambios
            brand_element = card.find('b', class_=lambda x: x and 'pod-title' in x)
            name_element = card.find('b', class_=lambda x: x and 'pod-subTitle' in x)
            
            brand = brand_element.text.strip() if brand_element else ""
            name = name_element.text.strip() if name_element else "Nombre no encontrado"
            product_name = f"{brand} {name}".strip()

            # --- Lógica para encontrar el precio MÁS BAJO (sin cambios, sigue funcionando) ---
            prices = []
            price_elements = card.select('div[id^="testId-pod-prices-"] li')
            
            for li in price_elements:
                # Buscamos en todos los posibles atributos de precio
                if li.get('data-normal-price'):
                    prices.append(float(li['data-normal-price']))
                if li.get('data-internet-price'):
                    prices.append(float(li['data-internet-price']))
                if li.get('data-cmr-price'):
                    prices.append(float(li['data-cmr-price']))
            
            # Nos quedamos con el menor precio encontrado
            lowest_price = min(prices) if prices else None
            
            if product_name != "Nombre no encontrado" and lowest_price is not None:
                scraped_data.append({
                    "Producto": product_name,
                    "Precio más bajo (S/)": lowest_price
                })

    except Exception as e:
        print(f"Ocurrió un error en la página {page_count}: {e}")
        # Guardamos el HTML para poder depurar
        with open(f"debug_page_{page_count}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"HTML guardado en 'debug_page_{page_count}.html'")
        break

    # --- Lógica de paginación (sin cambios, el ID del botón es el mismo) ---
    try:
        # Buscamos el botón de flecha derecha para ir a la siguiente página
        next_button = wait.until(EC.element_to_be_clickable((By.ID, "testId-pagination-bottom-arrow-right")))
        
        # Verificamos si el botón está habilitado. Si no, es la última página.
        if 'disabled' in next_button.get_attribute('class'):
            print("\nFin de la paginación. Se ha llegado a la última página.")
            break
            
        print("Cambiando a la siguiente página...")
        # Usamos JavaScript para hacer clic y evitar problemas de intercepción
        driver.execute_script("arguments[0].click();", next_button)
        page_count += 1
        time.sleep(4) # Damos un respiro un poco más largo antes de la siguiente iteración

    except Exception as e:
        print(f"\nNo se pudo pasar a la siguiente página. Posiblemente sea la última. Error: {e}")
        break

# --- Finalizar y mostrar resultados ---
driver.quit()

if scraped_data:
    df = pd.DataFrame(scraped_data)
    print("\n--- Total de Datos Extraídos ---")
    print(f"Se extrajeron {len(df)} productos en total.")
    print(df.head()) # Mostramos solo los primeros para no llenar la consola

    # --- CAMBIO 2: Nuevo nombre para el archivo de salida ---
    df.to_csv("precios_papel_higienico_tottus.csv", index=False, encoding='utf-8-sig')
    print("\n✅ Datos guardados exitosamente en 'precios_papel_higienico_tottus.csv'")
else:
    print("\nNo se pudo extraer ningún dato de producto válido.")