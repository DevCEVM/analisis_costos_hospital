CREATE DATABASE IF NOT EXISTS costos_hospital;
USE costos_hospital;
 
CREATE TABLE departamentos (
    departamento_id INT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    tipo VARCHAR(30) NOT NULL
);
 
CREATE TABLE categorias_costo (
    categoria_id INT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL
);
 
CREATE TABLE atenciones (
    mes DATE NOT NULL,
    departamento_id INT NOT NULL,
    num_atenciones INT NOT NULL,
    PRIMARY KEY (mes, departamento_id),
    FOREIGN KEY (departamento_id) REFERENCES departamentos(departamento_id)
);
 
CREATE TABLE costos (
    costo_id INT PRIMARY KEY,
    mes DATE NOT NULL,
    departamento_id INT NOT NULL,
    categoria_id INT NOT NULL,
    monto_real DECIMAL(14,2) NOT NULL,
    monto_presupuesto DECIMAL(14,2) NOT NULL,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(departamento_id),
    FOREIGN KEY (categoria_id) REFERENCES categorias_costo(categoria_id)
);
