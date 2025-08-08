# Guía para configurar un contenedor de scraping con Docker

## 📋 Requisitos y configuración inicial

### Instalar dependencias

```bash
python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt
```

### Actualizar dependencias

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

> **Nota**: Requiere `pip install pyinstaller pillow`

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

