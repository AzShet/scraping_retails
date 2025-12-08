from sqlalchemy import create_engine, text
import pandas as pd
import urllib.parse # Importante para manejar caracteres especiales en la conexión

# --- CONFIGURACIÓN SQL ---
# 1. Usamos r'' para que Python respete la barra invertida (\) del nombre del servidor
SERVER = r'AZSHET\SQLEXPRESS' 
DATABASE = 'TesisPrecios'

# OJO: Verifica en tu panel de control "Orígenes de datos ODBC" qué driver tienes.
# Si tienes el 18, cambia el 17 por 18. El 17 es el estándar más común.
DRIVER = 'ODBC Driver 17 for SQL Server' 

def cargar_datos(df):
    if df is None or df.empty:
        return

    # Construimos la cadena de conexión con parámetros extra
    # TrustServerCertificate=yes es VITAL porque en tu imagen esa casilla está marcada.
    params = urllib.parse.quote_plus(
        f'DRIVER={{{DRIVER}}};'
        f'SERVER={SERVER};'
        f'DATABASE={DATABASE};'
        f'Trusted_Connection=yes;'
        f'TrustServerCertificate=yes;'  # <--- ESTO ES LO QUE FALTABA SEGÚN TU IMAGEN
    )
    
    # SQLAlchemy requiere este formato específico para pyodbc
    connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
    
    try:
        # fast_executemany=True acelera muchísimo la carga de datos masivos
        engine = create_engine(connection_string, fast_executemany=True)
        
        print(f"--- Conectando a {SERVER} para cargar datos ---")
        
        with engine.begin() as conn: # Transacción automática
            for _, row in df.iterrows():
                # 1. Insertar/Buscar Supermercado
                conn.execute(text("""
                    IF NOT EXISTS (SELECT 1 FROM Dim_Supermercados WHERE Nombre = :sup)
                    INSERT INTO Dim_Supermercados (Nombre) VALUES (:sup)
                """), {'sup': row['Supermercado']})
                
                # 2. Insertar/Buscar Producto
                conn.execute(text("""
                    IF NOT EXISTS (SELECT 1 FROM Dim_Productos WHERE Nombre = :nom AND Categoria = :cat)
                    INSERT INTO Dim_Productos (Nombre, Categoria) VALUES (:nom, :cat)
                """), {'nom': row['Nombre'], 'cat': row['Categoria']})
                
                # 3. Obtener IDs
                id_sup = conn.execute(text("SELECT ID_Supermercado FROM Dim_Supermercados WHERE Nombre = :sup"), {'sup': row['Supermercado']}).scalar()
                id_prod = conn.execute(text("SELECT ID_Producto FROM Dim_Productos WHERE Nombre = :nom AND Categoria = :cat"), {'nom': row['Nombre'], 'cat': row['Categoria']}).scalar()
                
                # 4. Insertar Precio
                conn.execute(text("""
                    IF NOT EXISTS (SELECT 1 FROM Fact_Precios WHERE ID_Producto=:pid AND ID_Supermercado=:sid AND Fecha=:fec)
                    INSERT INTO Fact_Precios (ID_Producto, ID_Supermercado, Precio, Fecha)
                    VALUES (:pid, :sid, :prec, :fec)
                """), {'pid': id_prod, 'sid': id_sup, 'prec': row['Precio'], 'fec': row['Fecha']})
                
        print("✅ Carga a Base de Datos finalizada exitosamente.")
        
    except Exception as e:
        print(f"❌ Error crítico conectando a SQL: {e}")
        print("Posibles soluciones:")
        print("1. Verifica que el driver 'ODBC Driver 17 for SQL Server' esté instalado en Windows.")
        print("2. Asegúrate de haber ejecutado el script de creación de tablas en SSMS.")