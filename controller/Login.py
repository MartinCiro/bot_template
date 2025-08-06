from controller.BaseSelenium import BaseSelenium
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from os import getenv

class LoginDropi(BaseSelenium):
    """
    Clase encargada de ejecutar acciones automatizadas sobre la plataforma Zentria.
    
    Métodos disponibles:
        - login: inicia sesión con credenciales cargadas desde configuración.
    """

    def __init__(self) -> None:
        """Constructor de la clase. Hereda de BaseSelenium e inicializa el navegador."""
        load_dotenv()
        super().__init__()
        self.url_catalogo = self.helper.get_value("dropi", "url_catalogo")
        self.url_login = self.helper.get_value("dropi", "url_login")
        self.username  = getenv("USER")
        self.password  = getenv("PASSWD")
        self.login_attempts = 0 
        self.max_login_attempts = 3

    def login(self):
        """Login recursivo con contador de intentos."""
        if self.login_attempts >= self.max_login_attempts:
            return False
            
        self.login_attempts += 1
        avatar_xpath = "//img[contains(@class, 'rounded-circle')]"
        
        # Paso 1: Cargar página de login si es necesario
        if not self.wait_for_element(By.XPATH, "//input[@id='email']", timeout=3):
            self.open_url(self.url_catalogo)
            #self.open_url(self.url_login)

        if self.wait_for_element(By.XPATH, avatar_xpath, timeout=2):
            return True
        
        # Paso 2: Ingresar credenciales
        self.send_keys(By.XPATH, "//input[@id='email']", self.username)
        self.send_keys(By.XPATH, "//input[@id='password']", self.password)
        self.click(By.XPATH, '//button[@type="button"]')
        
        # Paso 3: Verificar éxito
        if self.wait_for_element(By.XPATH, avatar_xpath, timeout=8):
            return True
        
        return self.login()  # Llamada recursiva

