from sqlalchemy import create_engine, text
import pandas as pd

# --- CONFIGURACIÓN SQL ---
SERVER = 'TU_SERVIDOR'  # Ej: DESKTOP-CESAR\SQLEXPRESS
DATABASE = 'TesisPrecios'
DRIVER = 'ODBC Driver 17 for SQL Server'

def cargar_datos(df):
    if df is None or df.empty:
        return

    connection_string = f'mssql+pyodbc://@{SERVER}/{DATABASE}?driver={DRIVER}&trusted_connection=yes'
    
    try:
        engine = create_engine(connection_string)
        print("--- Iniciando Carga a SQL Server ---")
        
        with engine.begin() as conn: # Transacción automática
            for _, row in df.iterrows():
                # 1. Insertar/Buscar Supermercado
                conn.execute(text("""
                    IF NOT EXISTS (SELECT 1 FROM Dim_Supermercados WHERE Nombre = :sup)
                    INSERT INTO Dim_Supermercados (Nombre) VALUES (:sup)
                """), {'sup': row['Supermercado']})
                
                # 2. Insertar/Buscar Producto (Por Nombre y Categoría)
                conn.execute(text("""
                    IF NOT EXISTS (SELECT 1 FROM Dim_Productos WHERE Nombre = :nom AND Categoria = :cat)
                    INSERT INTO Dim_Productos (Nombre, Categoria) VALUES (:nom, :cat)
                """), {'nom': row['Nombre'], 'cat': row['Categoria']})
                
                # 3. Obtener IDs (Subconsultas rápidas)
                id_sup = conn.execute(text("SELECT ID_Supermercado FROM Dim_Supermercados WHERE Nombre = :sup"), {'sup': row['Supermercado']}).scalar()
                id_prod = conn.execute(text("SELECT ID_Producto FROM Dim_Productos WHERE Nombre = :nom AND Categoria = :cat"), {'nom': row['Nombre'], 'cat': row['Categoria']}).scalar()
                
                # 4. Insertar Precio (Evitar duplicados del día)
                conn.execute(text("""
                    IF NOT EXISTS (SELECT 1 FROM Fact_Precios WHERE ID_Producto=:pid AND ID_Supermercado=:sid AND Fecha=:fec)
                    INSERT INTO Fact_Precios (ID_Producto, ID_Supermercado, Precio, Fecha)
                    VALUES (:pid, :sid, :prec, :fec)
                """), {'pid': id_prod, 'sid': id_sup, 'prec': row['Precio'], 'fec': row['Fecha']})
                
        print("Carga a Base de Datos finalizada exitosamente.")
        
    except Exception as e:
        print(f"Error crítico conectando a SQL: {e}")
        print("Asegúrate de haber ejecutado el script 'modelos.sql' en SSMS primero.")