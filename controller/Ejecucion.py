from controller.BaseSelenium import BaseSelenium
from controller.Login import LoginDropi
from controller.Browse import Data_Products
from datetime import datetime, timedelta
from time import time
""" from controller.CLIPEmbedder import CLIPEmbedder
from controller.FAISSIndex import FAISSIndex
from controller.APIClient  import APIClient
from controller.Peticiones import Peticiones """
from os import environ
environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

class Ejecuciones(BaseSelenium):
    """
    Clase encargada de ejecutar acciones automatizadas sobre la plataforma Zentria.
    
    Métodos disponibles:
        - login: inicia sesión con credenciales cargadas desde configuración.
    """

    def __init__(self) -> None:
        super().__init__()
    
    def get_current_time(self):
        now = datetime.now()
        # Formato: dd/mm/yy, hora en 12h con AM/PM
        formatted_time = now.strftime("%d/%m/%y %I:%M:%S %p")
        return formatted_time
    
    def calculate_elapsed_time(self, start_time, end_time):
        elapsed = end_time - start_time
        # Convertir a formato legible (hh:mm:ss.microsegundos)
        elapsed_str = str(timedelta(seconds=elapsed))
        return elapsed_str

    def ejecuta(self):
        for ejecucion in range(3):  # Ejecutar el bloque completo 15 veces
            # Reiniciar el navegador cada 8 iteraciones
            if ejecucion > 0 and ejecucion % 4 == 0:
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

            inicio_ejecucion = time()
            self.helper.save_json("inicio.json", {"hora_inicio": self.get_current_time(), "ejecucion": ejecucion + 1}, append=True)

            # Configuración del while para reintentos de login
            intentos_login = 0
            max_intentos_login = 3
            login_exitoso = False
            
            while intentos_login < max_intentos_login and not login_exitoso:
                login_page = LoginDropi()
                if login_page.login():
                    login_exitoso = True
                    
                    # Si el login es exitoso, ejecutar data_products()
                    data_products = Data_Products()
                    data_products.data_products()
                else:
                    intentos_login += 1
                    print(f"⚠️ Intento de login {intentos_login} fallido")

            tiempo_ejecucion = self.calculate_elapsed_time(inicio_ejecucion, time())
            self.helper.save_json("Fin.json", {"hora_Fin": self.get_current_time(), "tiempo_ejecucion": tiempo_ejecucion}, append=True)

            if not login_exitoso:
                print("❌ No se pudo hacer login en esta ejecución")