# region importando librerias necesarias
from os import getcwd
from cryptography.fernet import Fernet
from requests import request, exceptions
from json import load, dump, JSONDecodeError
# endregion importando librerias necesarias

relativePath = getcwd()
KEYENCRYPT = "ecTNu1JkrN8WOEZQ667dOGOqBcS9Peh0RShN83l1WK0="
f = Fernet(KEYENCRYPT)
# endregion importando librerias necesarias

# region Creando una clase
class Helpers:
    # Contructores e inicializadores
    def __init__(self):
        self.__routeConfig = relativePath + "/config.json"

    # region Metodos
    # Nos ayuda para traer las rutas completas del config
    def get_routes(self, key, value = None):
        data = self.get_value(key, value)        
        fullpath = relativePath + data
        return fullpath
    
    def encriptar_data(self, valor: str):
        """
            Se encrypta un dato dado, en tipo str para
            hacer su encryptación a través de la llave
            recibida en el llamado del metodo
        - `Args:`
            - valor (str): Valor del metodo a encryptar
        - `Returns:`
            - str: Valor encryptado
        """
        token = f.encrypt(str.encode(valor)).decode("utf-8")
        return token
        
    def desencriptar_data(self, valor: str):
        """
            Toma la llave de encriptación, y el
            valor a desencriptar, y retorna el valor
            en formato str.
            - `Args:`
                - valor (str): Valor a desencriptar
            - `Returns:`
                - texto (str): Valor desencriptado en UTF8
        """
        texto = f.decrypt(valor)
        return texto.decode("utf-8")

    # Nos ayuda a extraer un valor del config
    def get_value(self, key, value = None):
        with open(self.__routeConfig, "r", encoding="utf-8") as file:
            config = load(file)

        return str(config.get(key, {}).get(value, "")) if value is not None else config.get(key, {})
        
    def get_json(self, ruta_archivo):
        """Carga un archivo JSON local y lo devuelve como un diccionario."""
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                return load(archivo)  # Convierte el JSON en un diccionario de Python
        except JSONDecodeError:
            print(f"❌ Error: El archivo '{ruta_archivo}' no tiene un formato JSON válido.")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        return None  # Retorna None si hay un error
    
    def save_json(self, ruta_archivo, datos, append=False):
        """Guarda un diccionario o lista en un archivo JSON. Si append es True, combina con datos existentes."""
        try:
            if append:
                datos_existentes = self.get_json(ruta_archivo) or {}

                # Combinamos según el tipo
                if isinstance(datos_existentes, dict) and isinstance(datos, dict):
                    datos_actualizados = {**datos_existentes, **datos}
                elif isinstance(datos_existentes, list) and isinstance(datos, list):
                    datos_actualizados = datos_existentes + datos
                else:
                    raise ValueError("❌ Los tipos de datos no coinciden o no son válidos para hacer append.")
            else:
                datos_actualizados = datos

            # Reutiliza la función original para guardar
            with open(ruta_archivo, "w", encoding="utf-8") as archivo:
                dump(datos_actualizados, archivo, ensure_ascii=False, indent=4)
                
        except Exception as e:
            print(f"❌ Error al guardar el archivo '{ruta_archivo}': {e}")


    def request_api(self, method, endpoint, data=None, token=None):
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        try:
            response = request(
                method=method,
                url=endpoint,
                headers=headers,
                json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                params=data if method == 'GET' else None
            )
            return response.json() if response.status_code in (200, 201) else None
        except exceptions.RequestException as e:
            print(f"Error en la solicitud {method}: {e}")
            return None
    
    # metodo para validar la respuesta del api
    def check_response(self, response) -> bool:
        if response and (response.get("status_code") == 200 or response.get("status_code") == 201):
            return True
        return False

    # endregion Metodos
# endregion