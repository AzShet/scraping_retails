import requests
from bs4 import BeautifulSoup

# url de emrcadolibre (ofertas
url = "https://tottus.falabella.com.pe/tottus-pe/category/cat13920469/Papeles"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)

# Verificar que la solicitud fue exitosa
if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    # Guardar el HTML en un archivo para analizarlo mejor
    with open("tottus_papeles.html", "w", encoding="utf-8") as file:
        file.write(soup.prettify())
    print("Archivo 'mercadolibre.html' guardado. Ábrelo en un navegador o en un␣ editor de texto para inspeccionar la estructura.")
else:
    print(f"Error al acceder a la página: {response.status_code}")