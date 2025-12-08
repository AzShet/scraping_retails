-- 1. Verificamos si la base de datos existe. Si no existe, la creamos.
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'TesisPrecios')
BEGIN
    CREATE DATABASE TesisPrecios;
END
GO

USE TesisPrecios;
GO

-- 2. Ahora creamos las tablas (Esto estaba bien, solo lo repito para que tengas todo junto)
CREATE TABLE Dim_Supermercados (
    ID_Supermercado INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(50) UNIQUE
);

CREATE TABLE Dim_Productos (
    ID_Producto INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(400),
    Categoria VARCHAR(100),
    CONSTRAINT UQ_Producto UNIQUE (Nombre, Categoria)
);

CREATE TABLE Fact_Precios (
    ID_Precio INT IDENTITY(1,1) PRIMARY KEY,
    ID_Producto INT,
    ID_Supermercado INT,
    Precio DECIMAL(10, 2),
    Fecha DATE,
    FOREIGN KEY (ID_Producto) REFERENCES Dim_Productos(ID_Producto),
    FOREIGN KEY (ID_Supermercado) REFERENCES Dim_Supermercados(ID_Supermercado)
);