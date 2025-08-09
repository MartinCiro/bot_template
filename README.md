# Guía para configurar un contenedor de scraping con Docker

## 📋 Requisitos y configuración inicial

### Instalar dependencias

```bash
python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt
```

### 2. Generación de clave de encriptación

```bash
from cryptography.fernet import Fernet

# Generar nueva clave (ejecutar en consola Python)
new_key = Fernet.generate_key().decode('utf-8')
print(f"CLAVE GENERADA: {new_key}")
```

### 3. Configuración de variables de entorno

Crea un archivo `.env` basado en `example.env` con esta estructura:

```bash
# Credenciales de Sofia Plus (obligatorias)
USER=tu_usuario_sofia
PASSWD=tu_password_sofia

# Configuración del navegador (True = modo invisible, False = mostrar)
HEADLESS=True
```

### Actualizar dependencias (Solo desarrollo)

```bash
python -m venv venv; venv\Scripts\activate; pip install pipreqs; pipreqs . --force
```

### Ejecutar proyecto

```bash
python main.py
```

## 🛠️ Procesos de automatización

### Conversión de archivo *".py"* a ejecutable *".exe"*

```bash
py -m PyInstaller --icon="ruta-absoluta-archivo-ico" ruta-abosulta-main-proyecto
```

#### 🚀 Opciones de compilación:

- `--onefile`: Genera un solo archivo ejecutable
- `--windowed`: Ejecución sin ventana de terminal

> **Nota**: Requiere `pip install pyinstaller pillow` y el reemplazo del key en el archivo helpers (linea 11)

🔧 **Herramienta útil**: [Complemento RPA para Firefox](https://addons.mozilla.org/en-US/firefox/addon/rpa/)

---

## 📂 **Estructura del Proyecto**

```

/core
  ├── /controller            # Lógica de negocio
  │   ├── utils              # Metodos reutilizables o compartidos
  ├── /plugins               # Carpeta contenedora de los plugins, librerías o ejecutables
  ├── /vendor                # Contiene archivos temp, imagenes, txt
```

#### 💡 **Creditos**

[Plantilla base](https://github.com/villalbaluis/arquitectura-bots-python) proporcionada por [Luis Villalba](https://github.com/villalbaluis)


## 🔄 Diagrama de Ejecución

```mermaid
graph TD
    A[Inicio] --> B[Crear entorno virtual]
    B --> C[Activar entorno]
    C --> D{¿Actualizar dependencias?}
    D -->|Sí| E[Ejecutar pipreqs --force]
    D -->|No| F[Instalar requirements.txt]
    E --> G[Ejecutar scraper]
    F --> G
    G --> H{¿Compilar a .exe?}
    H -->|Sí| I[Usar PyInstaller]
    H -->|No| J[Finalizar]
    I --> K[Generar ejecutable]
    K --> J

             +---------------------+
             |        Inicio       |
             +----------+----------+
                        |
                        v
             +----------+----------+
             |Crear entorno virtual|
             +----------+----------+
                        |
                        v
             +----------+----------+
             |   Activar entorno   |
             +----------+----------+
                        |
              +-------------------+
              |                   |
              v                   v
   +----------+----------+  +-----+-----+
   |Instalar dependencias|  | Actualizar|
   | (requirements.txt)  |  | (pipreqs) |
   +----------+----------+  +-----+-----+
              |                   |
              +---------+---------+
                        |
                        v
              +---------+---------+
              |  Ejecutar scraper |
              +---------+---------+
                        |
              +-------------------+
              |                   |
              v                   v
   +----------+----------+  +-----+-----+
   | Compilar a .exe     |  | Finalizar |
   | (PyInstaller)       |  |           |
   +----------+----------+  +-----------+
              |
              v
   +----------+----------+
   | Generar ejecutable  |
   | (--onefile/windowed)|
   +----------+----------+
              |
              v
   +----------+----------+
   |      Finalizar      |
   +---------------------+

