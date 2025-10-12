import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# URL de la categoría que quieres scrapear
url_metro = "https://www.metro.pe/frutas-y-verduras"

def obtener_productos_metro(url):
    with sync_playwright() as p:
        # Inicia el navegador. headless=False te permite ver lo que hace el bot.
        # Ponlo en True para que se ejecute en segundo plano.
        browser = p.chromium.launch(headless=False, slow_mo=50) 
        page = browser.new_page()
        
        print(f"Navegando a: {url}")
        page.goto(url, timeout=60000) # Aumenta el timeout a 60 segundos

        # ¡Paso clave! Esperamos a que un selector específico de producto aparezca.
        # Debes inspeccionar la página para encontrar el selector correcto.
        # En este caso, parece que cada producto está en un div con la clase 'product-card'
        print("Esperando a que los productos carguen...")
        page.wait_for_selector('div.product-card', timeout=30000)
        
        print("¡Productos cargados! Obteniendo el HTML...")
        # Obtenemos el contenido HTML final de la página
        html_final = page.content()
        
        # Cerramos el navegador
        browser.close()

        # Ahora usamos BeautifulSoup como siempre
        soup = BeautifulSoup(html_final, 'html.parser')
        
        # Buscamos todos los contenedores de productos
        productos = soup.find_all('div', class_='product-card')
        
        if not productos:
            print("No se encontraron productos con el selector 'div.product-card'.")
            return

        print(f"\n--- Se encontraron {len(productos)} productos ---")
        for producto in productos:
            # Extraemos el nombre del producto (ajusta el selector si es necesario)
            nombre_tag = producto.find('a', class_='product-item__name')
            nombre = nombre_tag.text.strip() if nombre_tag else "Nombre no encontrado"
            
            # Extraemos el precio (ajusta el selector si es necesario)
            precio_tag = producto.find('span', class_='product-prices__value')
            precio = precio_tag.text.strip() if precio_tag else "Precio no encontrado"
            
            print(f"Producto: {nombre} | Precio: {precio}")

# Ejecutamos la función
obtener_productos_metro(url_metro)