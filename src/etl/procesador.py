import pandas as pd
import os
import glob
from datetime import datetime

def limpiar_texto(texto):
    if not isinstance(texto, str): return "DESCONOCIDO"
    return texto.upper().strip().replace(" (X1)", "").replace(" UNIDAD", "")

def ejecutar_etl(input_folder="data/raw", output_folder="data/processed"):
    print("--- Iniciando Proceso ETL ---")
    
    # Buscar todos los archivos CSV en la carpeta raw
    archivos = glob.glob(f"{input_folder}/*.csv")
    lista_dfs = []
    fecha_hoy = datetime.now().date()

    for archivo in archivos:
        try:
            # Detectar supermercado y categoría basado en el nombre del archivo
            nombre_archivo = os.path.basename(archivo)
            if nombre_archivo.startswith("pv_"):
                supermercado = "Plaza Vea"
                categoria = nombre_archivo.replace("pv_", "").replace(".csv", "").replace("_", " ").title()
            elif nombre_archivo.startswith("tottus_"):
                supermercado = "Tottus"
                categoria = nombre_archivo.replace("tottus_", "").replace(".csv", "").replace("_", " ").title()
            else:
                continue # Saltar archivos que no sigan el patrón
            
            # Leer CSV (forzamos separador ; porque así lo configuramos en los scrapers)
            df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig')
            
            # Normalizar columnas
            df.columns = [c.lower() for c in df.columns]
            df = df.rename(columns={'producto': 'Nombre', 'precio': 'Precio'})
            
            # Añadir metadatos
            df['Supermercado'] = supermercado
            df['Categoria'] = categoria
            df['Fecha'] = fecha_hoy
            
            # Limpieza básica
            df['Nombre'] = df['Nombre'].apply(limpiar_texto)
            df = df.dropna(subset=['Precio']) # Eliminar si no tiene precio
            
            lista_dfs.append(df[['Fecha', 'Supermercado', 'Categoria', 'Nombre', 'Precio']])
            
        except Exception as e:
            print(f"Error procesando {archivo}: {e}")

    if lista_dfs:
        os.makedirs(output_folder, exist_ok=True)
        consolidado = pd.concat(lista_dfs, ignore_index=True)
        # Eliminar duplicados exactos
        consolidado = consolidado.drop_duplicates()
        
        output_path = f"{output_folder}/consolidado_precios.csv"
        consolidado.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"ETL Completado. Datos guardados en: {output_path}")
        return consolidado
    else:
        print("No se encontraron datos para procesar.")
        return None