-- ============================
-- 📘 MULTAS_APP DATABASE SETUP
-- ============================

-- Crear la base de datos
DROP DATABASE IF EXISTS multas_app;
CREATE DATABASE multas_app CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE multas_app;

-- ============================
-- TABLAS PRINCIPALES
-- ============================

-- Tabla de colegiaturas / agremiados
CREATE TABLE colegiaturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    estado ENUM('PAGADO', 'NO PAGADO') DEFAULT 'NO PAGADO',
    observaciones TEXT
);

-- Tabla de asambleas
CREATE TABLE asambleas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    fecha DATE NOT NULL,
    costo DECIMAL(10,2) NOT NULL
);

-- Tabla de asistencias
CREATE TABLE asistencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    colegiatura_id INT NOT NULL,
    asamblea_id INT NOT NULL,
    presente BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (colegiatura_id) REFERENCES colegiaturas(id) ON DELETE CASCADE,
    FOREIGN KEY (asamblea_id) REFERENCES asambleas(id) ON DELETE CASCADE,
    UNIQUE KEY unique_asistencia (colegiatura_id, asamblea_id)
);

-- ============================
-- DATOS DE EJEMPLO
-- ============================

-- Agremiados simulados (CAJ)
INSERT INTO colegiaturas (nombre, estado, observaciones) VALUES
('1', 'NO PAGADO', ''),
('2', 'PAGADO', 'Regularización parcial'),
('3', 'NO PAGADO', ''),
('4', 'PAGADO', ''),
('5', 'NO PAGADO', 'Debe multa de 2 asambleas'),
('6', 'NO PAGADO', ''),
('7', 'PAGADO', ''),
('8', 'NO PAGADO', ''),
('9', 'NO PAGADO', ''),
('10', 'NO PAGADO', '');

-- Asambleas registradas
INSERT INTO asambleas (nombre, fecha, costo) VALUES
('00 Ordinaria', '2024-04-02', 25.75),
('01 Ordinaria', '2024-04-25', 25.75),
('02 Ordinaria', '2024-07-04', 25.75),
('03 Extraordinaria', '2024-08-08', 25.75),
('04 Extraordinaria', '2024-09-18', 25.75),
('05 Ordinaria', '2024-10-10', 25.75);

-- Asistencias simuladas
INSERT INTO asistencias (colegiatura_id, asamblea_id, presente) VALUES
(1, 1, TRUE), (1, 2, FALSE), (1, 3, TRUE), (1, 4, FALSE), (1, 5, TRUE), (1, 6, TRUE),
(2, 1, TRUE), (2, 2, TRUE), (2, 3, TRUE), (2, 4, TRUE), (2, 5, TRUE), (2, 6, TRUE),
(3, 1, FALSE), (3, 2, FALSE), (3, 3, FALSE), (3, 4, FALSE), (3, 5, FALSE), (3, 6, FALSE),
(4, 1, TRUE), (4, 2, FALSE), (4, 3, TRUE), (4, 4, FALSE), (4, 5, TRUE), (4, 6, FALSE),
(5, 1, TRUE), (5, 2, TRUE), (5, 3, TRUE), (5, 4, FALSE), (5, 5, FALSE), (5, 6, TRUE);
