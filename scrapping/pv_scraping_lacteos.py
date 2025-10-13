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
# Descomenta la siguiente línea si no quieres que se abra la ventana del navegador
# options.add_argument('--headless') 
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Inicializa el WebDriver de forma moderna
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# URL de la página a scrapear
url = "https://www.plazavea.com.pe/lacteos-y-huevos"
driver.get(url)

# Listas para almacenar los datos
productos = []
precios = []

print("Iniciando el scraping...")

while True:
    try:
        # Espera a que el contenedor de los productos esté presente en la página
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "showcase-grid"))
        )
        
        # Pequeña pausa para asegurar que todo el contenido dinámico cargue
        time.sleep(2) 

        # Obtiene el HTML de la página actual
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Encuentra todos los contenedores de productos
        # Se usa la clase 'ga-product-item' que es más específica para cada producto
        items = soup.find_all('div', class_='ga-product-item')

        if not items:
            print("No se encontraron más productos en la página.")
            break

        # Extrae el nombre y el precio de cada producto
        for item in items:
            # El nombre del producto está en el atributo 'data-ga-name'
            nombre = item.get('data-ga-name')
            if nombre:
                productos.append(nombre)
            else:
                productos.append("No disponible")

            # El precio del producto está en el atributo 'data-ga-price'
            precio = item.get('data-ga-price')
            if precio:
                precios.append(float(precio))
            else:
                precios.append(0.0)
        
        # --- Manejo de la Paginación ---
        # Busca el botón "siguiente"
        # Usamos un selector CSS para encontrar el span que no tiene la clase 'disabled'
        next_button = driver.find_element(By.CSS_SELECTOR, ".pagination__item.page-control.next:not(.disabled)")
        
        # Imprime la página actual que se está procesando
        current_page = driver.find_element(By.CSS_SELECTOR, ".pagination__item.page-number.active").text
        print(f"Productos de la página {current_page} extraídos.")
        
        # Hace clic en el botón "siguiente"
        driver.execute_script("arguments[0].click();", next_button)

    except Exception as e:
        # Si no se encuentra el botón "siguiente" o hay otro error, termina el bucle
        print("No hay más páginas o se produjo un error al cambiar de página. Finalizando scraping.")
        # print(f"Error: {e}") # Descomenta para depurar
        break

# Cierra el navegador
driver.quit()

# --- Creación del DataFrame y exportación a CSV ---
if productos:
    # Crea un DataFrame con los datos recolectados
    df = pd.DataFrame({
        'Producto': productos,
        'Precio': precios
    })

    # Guarda el DataFrame en un archivo CSV
    df.to_csv('PV_lacteos.csv', index=False, encoding='utf-8-sig', sep=';')

    print("\nScraping completado con éxito.")
    print(f"Se extrajeron {len(productos)} productos.")
    print("Los datos se han guardado en 'PV_lacteos.csv'")
    # Imprime las primeras filas del DataFrame
    print("\nMuestra de los datos:")
    print(df.head())
else:
    print("No se pudo extraer ningún producto.")