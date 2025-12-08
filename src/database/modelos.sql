USE master;
GO

-- 1. Verificar y crear la base de datos
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'TesisPrecios')
BEGIN
    CREATE DATABASE TesisPrecios;
    PRINT 'Base de datos TesisPrecios creada exitosamente.';
END
ELSE
BEGIN
    PRINT 'La base de datos TesisPrecios ya existe.';
END
GO

USE TesisPrecios;
GO

-- 2. Crear Tabla Supermercados
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Dim_Supermercados')
BEGIN
    CREATE TABLE Dim_Supermercados (
        ID_Supermercado INT IDENTITY(1,1) PRIMARY KEY,
        Nombre VARCHAR(50) UNIQUE
    );
    PRINT 'Tabla Dim_Supermercados creada.';
END
GO

-- 3. Crear Tabla Productos
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Dim_Productos')
BEGIN
    CREATE TABLE Dim_Productos (
        ID_Producto INT IDENTITY(1,1) PRIMARY KEY,
        Nombre VARCHAR(400),
        Categoria VARCHAR(100),
        CONSTRAINT UQ_Producto UNIQUE (Nombre, Categoria)
    );
    PRINT 'Tabla Dim_Productos creada.';
END
GO

-- 4. Crear Tabla Precios
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Fact_Precios')
BEGIN
    CREATE TABLE Fact_Precios (
        ID_Precio INT IDENTITY(1,1) PRIMARY KEY,
        ID_Producto INT,
        ID_Supermercado INT,
        Precio DECIMAL(10, 2),
        Fecha DATE,
        FOREIGN KEY (ID_Producto) REFERENCES Dim_Productos(ID_Producto),
        FOREIGN KEY (ID_Supermercado) REFERENCES Dim_Supermercados(ID_Supermercado)
    );
    PRINT 'Tabla Fact_Precios creada.';
END
GO