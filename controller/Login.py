from time import sleep
from controller.Config import Config
from selenium.webdriver.common.by import By

class LoginSena(Config):
    """
    Clase encargada de ejecutar acciones automatizadas sobre la plataforma Zentria.
    
    Métodos disponibles:
        - login: inicia sesión con credenciales cargadas desde configuración.
    """

    def __init__(self) -> None:
        """Constructor de la clase. Hereda de BaseSelenium e inicializa el navegador."""
        super().__init__()
        self.login_attempts = 0 
        self.max_login_attempts = 2

    def login(self):
        """Login recursivo con contador de intentos."""
        if self.login_attempts >= self.max_login_attempts:
            return False
            
        self.login_attempts += 1
        
        # Verificar si ya estamos logueados (fuera del iframe)
        avatar_xpath = "//h4"
        if self.wait_for_element(By.XPATH, avatar_xpath, timeout=2):
            return True
        
        self.open_url(self.url_login)

        try:
            # 1. Cambiar al iframe
            if not self.switch_to_frame("registradoBox1"):
                if self.wait_for_element(By.XPATH, avatar_xpath, timeout=8):
                    self.driver.switch_to.default_content()  # Asegurarse de salir del iframe
                    return True
                raise Exception("No se pudo cambiar al iframe")
            
            # 2. Interactuar con elementos DENTRO del iframe (XPaths normales)
            self.send_keys(By.XPATH, "//input[@id='username']", self.username)
            self.send_keys(By.XPATH, "//input[@type='password']", self.password)
            self.send_keys(By.XPATH, "//input[@name='ingresar']", None, clear=False, special_key="ENTER")
            
            # 3. Volver al contexto principal
            self.driver.switch_to.default_content()
            
        except Exception as e:
            try:
                # Si falla, intentar cambiar al iframe de nuevo
                self.driver.switch_to.default_content()
            except Exception:
                pass
            return self.login()  
        
        # Verificar si el login fue exitoso
        if self.wait_for_element(By.XPATH, avatar_xpath, timeout=2):
            return True
        
        return self.login()  # Llamada recursiva si falla