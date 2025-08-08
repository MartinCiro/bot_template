from controller.BaseSelenium import BaseSelenium
from controller.Login import LoginSena
from controller.Browse import Browse_web

from selenium.webdriver.common.by import By
from time import sleep, time
""" from controller.CLIPEmbedder import CLIPEmbedder
from controller.FAISSIndex import FAISSIndex
from controller.APIClient  import APIClient
from controller.Peticiones import Peticiones """
from os import environ
environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

class Ejecuciones(BaseSelenium):
    """
    Clase encargada de ejecutar acciones automatizadas sobre la plataforma Sena.
    
    Métodos disponibles:
        - login: inicia sesión con credenciales cargadas desde configuración.
    """

    def __init__(self) -> None:
        super().__init__()

    def ejecuta(self):
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                # Limpiar la instancia singleton para forzar nueva creación
                BaseSelenium._instance = None
                BaseSelenium._initialized = False

                # Recrear la instancia
                self.__init__()
            except Exception as e:
                print(f"Error al reiniciar el navegador: {e}")
                # Continuar de todos modos

        # Configuración del while para reintentos de login
        intentos_login = 0
        login_exitoso = False
        
        navigator = Browse_web()
        while intentos_login < 3 and not login_exitoso:
            login_page = LoginSena()
            if login_page.login():
                login_exitoso = True
                print(f"✅ Login exitoso en el intento {intentos_login + 1}")
                sleep(8)
                navigator.navigate_certified()
                continue
                
            else:
                intentos_login += 1
                print(f"⚠️ Intento de login {intentos_login} fallido")

        if not login_exitoso:
            print("❌ No se pudo hacer login en esta ejecución")