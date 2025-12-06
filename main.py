import sys
import os

# Asegurar que Python encuentre los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scrapers.plazavea import scrapear_plazavea
from src.scrapers.tottus import scrapear_tottus
from src.etl.procesador import ejecutar_etl
from src.database.cargador_sql import cargar_datos

# --- CONFIGURACIÓN DE TAREAS ---
# Aquí defines qué quieres scrapear. ¡Puedes agregar más fácilmente!
TAREAS_PLAZAVEA = [
    ("https://www.plazavea.com.pe/carnes-aves-y-pescados", "Carnes"),
    ("https://www.plazavea.com.pe/lacteos-y-huevos", "Lacteos"),
    ("https://www.plazavea.com.pe/bebidas", "Bebidas"),
    # Agrega el resto de tus URLs aquí...
]

TAREAS_TOTTUS = [
    ("https://tottus.falabella.com.pe/tottus-pe/category/CATG14245/Papel-Higienico", "Papeles"),
    ("https://tottus.falabella.com.pe/tottus-pe/search?Ntt=huevos", "Huevos"),
    # Agrega el resto de tus URLs aquí...
]

def main():
    print("========================================")
    print("   SISTEMA DE EXTRACCIÓN DE PRECIOS")
    print("========================================\n")

    # 1. FASE DE EXTRACCIÓN
    # ------------------------------------------------
    for url, categoria in TAREAS_PLAZAVEA:
        scrapear_plazavea(url, categoria)
        
    for url, categoria in TAREAS_TOTTUS:
        scrapear_tottus(url, categoria)

    # 2. FASE DE TRANSFORMACIÓN (ETL)
    # ------------------------------------------------
    df_final = ejecutar_etl()

    # 3. FASE DE CARGA (LOAD)
    # ------------------------------------------------
    if df_final is not None:
        cargar_datos(df_final)
    
    print("\n========================================")
    print("   PROCESO TERMINADO")
    print("========================================")

if __name__ == "__main__":
    main()