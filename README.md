# Guía para configurar un contenedor de scrapping con Docker

## Instalar dependencias

El siguiente comando crea, activa e instala lo necesario:

```bash
python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt
```

## Actualizar dependencias

El siguiente comando crea, activa y actualiza las dependencias necesarias:

```bash
python -m venv venv; venv\Scripts\activate; pip install pipreqs; pipreqs . --force 
```

## 📌 Comentarios útiles para los procesos de automatización

### Conversión de archivo *".py"* a ejecutable *".exe"*

```bash
py -m PyInstaller --icon="ruta-absoluta-archivo-ico" ruta-abosulta-main-proyecto
```

#### 🚀 Opciones de compilado

* **--onefile** Crea el ejecutable en un solo archivo comprimido que lleva el nombre del archivo main pasado, con extensión .exe
* **--windowed** Dehabilita las ventanas de CMD durante la ejecución del programa.

##### 📄 Nota

Debe tener instalada la libreria **Pyinstaller** antes de realizar este paso. **(pip install pyinstaller)**

Herrramienta xpath: https://addons.mozilla.org/en-US/firefox/addon/rpa/

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