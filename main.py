import sys
import os

# Aseguramos que Python encuentre la carpeta src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importamos las funciones que creamos en los pasos anteriores
from src.scrapers.plazavea import scrapear_plazavea
from src.scrapers.tottus import scrapear_tottus
from src.etl.procesador import ejecutar_etl
from src.database.cargador_sql import cargar_datos

# ==========================================
# AQUÍ ESTÁN TUS ENLACES (CONFIGURACIÓN)
# ==========================================
# He sacado estas URLs directamente de tus archivos pv_scraping_*.py
TAREAS_PLAZAVEA = [
    # (URL, Nombre de la Categoría para el reporte)
    ("https://www.plazavea.com.pe/lacteos-y-huevos", "Lacteos"),         # De pv_scraping_lacteos.py
    ("https://www.plazavea.com.pe/frutas-y-verduras", "Frutas"),         # De pv_scraping_frutas_verduras.py
    ("https://www.plazavea.com.pe/carnes-aves-y-pescados", "Carnes"),    # De pv_scraping_carnes.py
    ("https://www.plazavea.com.pe/bebidas", "Bebidas"),                  # De pv_scraping_bebidas.py
    ("https://www.plazavea.com.pe/cuidado-personal-y-salud", "Cuidado Personal"), # De pv_scraping_cuidado_personal.py
    ("https://www.plazavea.com.pe/quesos-y-fiambres", "Quesos"),         # De pv_scraping_quesos.py
]

# He sacado estas URLs directamente de tus archivos scrapping_*.py
TAREAS_TOTTUS = [
    # (URL, Nombre de la Categoría para el reporte)
    ("https://tottus.falabella.com.pe/tottus-pe/category/cat13380487/Despensa", "Despensa"), # De scrapping_despensa.py
    ("https://tottus.falabella.com.pe/tottus-pe/category/cat13380486/Bebidas--aguas-y-jugos", "Bebidas"), # De scrapping_bebidas.py
    ("https://tottus.falabella.com.pe/tottus-pe/category/CATG14245/Papel-Higienico", "Papel Higienico"), # De scrapping_papeles.py
    ("https://tottus.falabella.com.pe/tottus-pe/search?Ntt=huevos", "Huevos"), # De scrapping_huevos.py
]

def main():
    print("========================================")
    print("   SISTEMA DE EXTRACCIÓN DE PRECIOS")
    print("========================================\n")

    # 1. FASE DE EXTRACCIÓN (SCRAPING)
    # ------------------------------------------------
    print(">>> INICIANDO SCRAPING PLAZA VEA...")
    for url, categoria in TAREAS_PLAZAVEA:
        # Aquí la función 'scrapear_plazavea' recibe la URL de la lista
        scrapear_plazavea(url, categoria)
        
    print("\n>>> INICIANDO SCRAPING TOTTUS...")
    for url, categoria in TAREAS_TOTTUS:
        # Aquí la función 'scrapear_tottus' recibe la URL de la lista
        scrapear_tottus(url, categoria)

    # 2. FASE DE TRANSFORMACIÓN (ETL)
    # ------------------------------------------------
    print("\n>>> INICIANDO LIMPIEZA Y UNIFICACIÓN DE DATOS...")
    df_final = ejecutar_etl()

    # 3. FASE DE CARGA (LOAD SQL)
    # ------------------------------------------------
    if df_final is not None:
        print("\n>>> INICIANDO CARGA A SQL SERVER...")
        cargar_datos(df_final)
    else:
        print("\n!!! ALERTA: No se generaron datos para cargar.")
    
    print("\n========================================")
    print("   PROCESO TERMINADO")
    print("========================================")

if __name__ == "__main__":
    main()