import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- Configuración de Selenium ---
options = webdriver.ChromeOptions()
# Descomenta la siguiente línea para ver lo que hace el navegador
# options.add_argument('--headless') 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# Añadimos un user-agent para simular un navegador real y evitar bloqueos
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = "https://tottus.falabella.com.pe/tottus-pe/search?Ntt=huevos"

print("Accediendo a la página...")
driver.get(url)

# --- Espera a que los productos carguen (VERSIÓN MEJORADA) ---
try:
    print("Esperando a que cargue el contenido dinámico...")
    wait = WebDriverWait(driver, 20)
    
    # --- CAMBIO CLAVE 1: Espera más específica ---
    # En lugar de esperar el contenedor general, esperamos a que la PRIMERA tarjeta de producto
    # (identificada por el atributo 'pod-layout') sea visible. Esto es mucho más fiable.
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[pod-layout]")))
    
    print("¡Contenido cargado con éxito!")
    
    # A veces, las páginas cargan productos a medida que haces scroll (lazy loading).
    # Hacemos un pequeño scroll para asegurarnos de cargar más elementos.
    driver.execute_script("window.scrollTo(0, 1000);")
    time.sleep(3) # Damos tiempo para que el scroll cargue nuevos productos

except Exception as e:
    print(f"No se pudo cargar la página o encontrar los productos. Error: {e}")
    # Guardamos el HTML para poder depurar qué está viendo Selenium
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Se ha guardado el HTML actual en 'debug_page.html' para análisis.")
    driver.quit()
    exit()

# --- Extracción del HTML ---
html_content = driver.page_source
driver.quit()

# --- Análisis del HTML con BeautifulSoup ---
soup = BeautifulSoup(html_content, 'html.parser')

# --- CAMBIO CLAVE 2: Selector más robusto para los productos ---
# Usamos el mismo atributo 'pod-layout' para encontrar TODAS las tarjetas de productos.
product_cards = soup.find_all('div', attrs={'pod-layout': True})

# --- Procesamiento de los datos ---
scraped_data = []

print(f"Se encontraron {len(product_cards)} productos. Extrayendo datos...")

if not product_cards:
    print("No se encontraron tarjetas de productos. Revisa 'debug_page.html' si se creó.")
    exit()

for card in product_cards:
    name_element = card.find('b', class_=lambda x: x and 'pod-subTitle' in x)
    product_name = name_element.text.strip() if name_element else "Nombre no encontrado"
    
    original_price_element = card.find('li', attrs={'data-normal-price': True})
    
    product_price = None
    if original_price_element:
        product_price = original_price_element['data-normal-price']
    else:
        internet_price_element = card.find('li', attrs={'data-internet-price': True})
        if internet_price_element:
            product_price = internet_price_element['data-internet-price']

    if product_name != "Nombre no encontrado" and product_price:
        try:
            # Aseguramos que el precio sea un número flotante
            price_float = float(product_price)
            scraped_data.append({
                "Producto": product_name,
                "Precio Original (S/)": price_float
            })
        except (ValueError, TypeError):
            print(f"No se pudo convertir el precio '{product_price}' para el producto '{product_name}'")


# --- Mostrar los resultados con Pandas ---
if scraped_data:
    df = pd.DataFrame(scraped_data)
    print("\n--- Datos Extraídos ---")
    print(df)

    df.to_csv("precios_huevos_tottus.csv", index=False, encoding='utf-8-sig')
    print("\n✅ Datos guardados en 'precios_huevos_tottus.csv'")
else:
    print("\nNo se pudo extraer ningún dato de producto válido.")