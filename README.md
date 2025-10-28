# 🧾 MultasApp — Sistema de Control de Asambleas y Multas

**MultasApp** es una aplicación web desarrollada con **Flask (Python)** y **MySQL** que permite gestionar la asistencia de agremiados a asambleas, calcular multas por inasistencia y administrar toda la información desde un panel administrativo.

---

## 🚀 Características principales

- 🔍 **Búsqueda por número de colegiatura (CAJ)** para verificar multas.
- 🧮 Cálculo automático de multas por inasistencia.
- 🧑‍💼 **Panel administrativo completo** con:
  - Creación, visualización y eliminación de asambleas.
  - Gestión de colegiados/agremiados.
  - Modificación de estado de pago y observaciones.
  - Actualización en tiempo real de la base de datos.
- 📊 Interfaz moderna con **TailwindCSS** y **JavaScript (AJAX)**.
- 🗄️ Integración directa con **MySQL**.

---

## 🛠️ Tecnologías utilizadas

| Tipo | Tecnología |
|------|-------------|
| Backend | Flask (Python 3.10+) |
| Frontend | HTML5, TailwindCSS, JavaScript (Fetch API) |
| Base de datos | MySQL 8+ |
| Entorno virtual | venv |
| Servidor local | Flask Dev Server (5000) |

---

## 🧩 Estructura del proyecto

```

multas_app/
│
├── app.py                     # Archivo principal Flask
├── config.py                  # Configuración de la base de datos MySQL
├── requirements.txt           # Dependencias del proyecto
│
├── static/
│   └── js/
│       ├── buscar.js          # Lógica de búsqueda en la página principal
│       └── admin.js           # Lógica dinámica del panel admin
│
├── templates/
│   ├── index.html             # Vista principal (búsqueda de multas)
│   ├── admin.html             # Panel administrativo
│
├── database.sql               # Script SQL para crear la base de datos y tablas
└── README.md                  # Documentación del proyecto

````

---

## ⚙️ Instalación y configuración

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/<TU_USUARIO>/multas_app.git
cd multas_app
````

### 2️⃣ Crear y activar un entorno virtual

```bash
python -m venv .venv
.venv\Scripts\activate       # En Windows
source .venv/bin/activate    # En Linux/Mac
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:

```txt
flask
mysql-connector-python
```

---

## 🧱 Configuración de la base de datos MySQL

### 🔧 Crear la base de datos y tablas

Conéctate a MySQL e ingresa:

```sql
CREATE DATABASE multas_app CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE multas_app;

-- Tabla de colegiaturas/agremiados
CREATE TABLE colegiaturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    estado ENUM('PAGADO','NO PAGADO') DEFAULT 'NO PAGADO',
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
    colegiatura_id INT,
    asamblea_id INT,
    presente BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (colegiatura_id) REFERENCES colegiaturas(id) ON DELETE CASCADE,
    FOREIGN KEY (asamblea_id) REFERENCES asambleas(id) ON DELETE CASCADE
);

-- Datos de ejemplo
INSERT INTO colegiaturas (nombre, estado) VALUES
('1','NO PAGADO'),
('2','PAGADO'),
('3','NO PAGADO'),
('4','NO PAGADO');

INSERT INTO asambleas (nombre, fecha, costo) VALUES
('00 Ordinaria', '2024-04-02', 25.75),
('01 Ordinaria', '2024-04-25', 25.75),
('02 Ordinaria', '2024-07-04', 25.75),
('03 Extraordinaria', '2024-08-08', 25.75),
('04 Extraordinaria', '2024-09-18', 25.75),
('05 Ordinaria', '2024-10-10', 25.75);
```

---

## 🔑 Configuración de conexión a MySQL (`config.py`)

```python
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="CAJ25@as",
        database="multas_app"
    )
```

---

## ▶️ Ejecución del servidor

```bash
python app.py
```

Abre en tu navegador:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🌐 Rutas y endpoints

### Usuario

| Método | Ruta      | Descripción                                           |
| ------ | --------- | ----------------------------------------------------- |
| `GET`  | `/`       | Página principal de búsqueda                          |
| `POST` | `/buscar` | Busca por número de CAJ y devuelve detalles de multas |

### Panel Admin

| Método | Ruta                                      | Descripción                                             |
| ------ | ----------------------------------------- | ------------------------------------------------------- |
| `GET`  | `/admin`                                  | Vista del panel de administración                       |
| `GET`  | `/api/datos`                              | Devuelve JSON con asambleas, colegiaturas y asistencias |
| `POST` | `/crear_asamblea`                         | Crea una nueva asamblea                                 |
| `POST` | `/borrar_asamblea/<id>`                   | Elimina una asamblea existente                          |
| `POST` | `/agregar_agremiado`                      | Agrega un nuevo agremiado por número de CAJ             |
| `POST` | `/actualizar_asistencia/<caj>/<asamblea>` | Marca asistencia de un agremiado                        |
| `POST` | `/actualizar_observacion/<caj>`           | Actualiza observaciones o estado                        |

---

## 🧮 Lógica de cálculo de multas

1. El usuario ingresa su número de **CAJ** en el campo de búsqueda.
2. Flask consulta las asistencias de ese agremiado.
3. Por cada asamblea **no asistida (presente = FALSE)** se suma el costo como multa.
4. El total se muestra en pantalla junto con el detalle por asamblea.

---

## 🧑‍💼 Panel de administración

* Permite crear o eliminar asambleas.
* Muestra **todas las colegiaturas** con su asistencia en cada asamblea.
* Permite marcar o desmarcar asistencia con un clic.
* Permite editar estado de pago y observaciones.
* Actualización en tiempo real mediante `fetch` (sin recargar la página).

---

## 📸 Capturas sugeridas

Agrega en tu repositorio una carpeta `docs/` con las imágenes:

```
docs/
 ├── index.png
 ├── admin_panel.png
 └── detalle_multas.png
```

Y referencia en el README:

```markdown
![Pantalla principal](docs/index.png)
![Panel admin](docs/admin_panel.png)
```

---

## 🧾 Licencia

Este proyecto está licenciado bajo la **MIT License**.
Eres libre de usarlo, modificarlo y distribuirlo, siempre y cuando mantengas el crédito correspondiente.

---

## 👨‍💻 Autor

Desarrollado por **[Tu Nombre]**
📧 Contacto: [tuemail@dominio.com](mailto:tuemail@dominio.com)
🐙 GitHub: [https://github.com/TU_USUARIO](https://github.com/TU_USUARIO)
