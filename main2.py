import sys
import os
import pandas as pd # Importamos pandas directamente

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importamos solo el cargador, ya no necesitamos los scrapers por ahora
from src.database.cargador_sql import cargar_datos

def main():
    print("========================================")
    print("   SISTEMA DE CARGA (SOLO SQL)")
    print("========================================\n")

    # --- PASO 1 Y 2 OMITIDOS (YA TIENES LOS DATOS) ---
    # Comentamos todo esto para no perder tiempo
    """
    for url, categoria in TAREAS_PLAZAVEA:
        scrapear_plazavea(url, categoria)
        
    for url, categoria in TAREAS_TOTTUS:
        scrapear_tottus(url, categoria)

    df_final = ejecutar_etl()
    """

    # --- PASO 3: CARGA DIRECTA ---
    print(">>> LEYENDO DATOS YA PROCESADOS...")
    
    # Ruta donde el ETL guardó el archivo en la ejecución anterior
    archivo_procesado = "data/processed/consolidado_precios.csv"
    
    if os.path.exists(archivo_procesado):
        # Leemos el CSV directamente
        df_final = pd.read_csv(archivo_procesado)
        print(f"✅ Archivo cargado: {len(df_final)} registros encontrados.")
        
        print("\n>>> INICIANDO CARGA A SQL SERVER...")
        cargar_datos(df_final)
    else:
        print(f"❌ Error: No se encuentra el archivo {archivo_procesado}")
        print("   Ejecuta el ETL primero o revisa la carpeta data/processed.")
    
    print("\n========================================")
    print("   PROCESO TERMINADO")
    print("========================================")

if __name__ == "__main__":
    main()