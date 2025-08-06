from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium import webdriver # type: ignore
from selenium.common.exceptions import TimeoutException, WebDriverException # type: ignore
from selenium.webdriver.firefox.service import Service # type: ignore
from selenium.webdriver.firefox.options import Options # type: ignore
from controller.utils.Helpers import Helpers
from controller.GeckoDriverInstaller import GeckoDriverInstaller
from typing import List
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains # type: ignore
from dotenv import load_dotenv
from os import getenv
load_dotenv()

class BaseSelenium:
    _instance = None  # Para implementar patrón singleton
    
    def __new__(cls, *args, **kwargs):
        """Implementa patrón singleton para evitar múltiples instancias"""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.helper = Helpers()
        

        if getattr(BaseSelenium, "_initialized", False):
            self.driver = BaseSelenium.driver
            self.wait = BaseSelenium.wait
            return
                
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.set_preference("dom.popup_maximum", 0)
        options.set_preference("dom.disable_beforeunload", True)
        options.set_preference("javascript.enabled", True)

        driver_installer = GeckoDriverInstaller(self.helper.get_routes("SELENIUM", "driver_path"))
        driver_installer.install()
        driver_path = driver_installer.get_driver_path()

        headle = getenv("HEADLESS", "False").lower() in ("true", "1", "yes")
        if headle:
            options.add_argument("--headless")

        service = Service(
            executable_path=driver_path,
            log_path="geckodriver.log"
        )

        try:
            BaseSelenium.driver = webdriver.Firefox(service=service, options=options)
            BaseSelenium.wait = WebDriverWait(BaseSelenium.driver, 10)
            BaseSelenium.driver.implicitly_wait(10)
            if not headle:
                BaseSelenium.driver.maximize_window()
                
            BaseSelenium._initialized = True
            self.driver = BaseSelenium.driver
            self.wait = BaseSelenium.wait
        except WebDriverException as e:
            raise Exception(f"No se pudo iniciar el navegador: {str(e)}")

    def open_url(self, url: str, tab_index: int = None):
        """
        Abre una URL en una pestaña específica o en la actual.
        Args:
            url: URL a abrir
            tab_index: Índice de la pestaña (0-based). Si es None, usa la actual.
        """
        if not self.is_browser_alive():
            self.__init__()  # Recrear instancia si el navegador murió
            
        if tab_index is not None:
            if len(self.driver.window_handles) <= tab_index:
                self.driver.execute_script("window.open('about:blank', '_blank');")
            self.driver.switch_to.window(self.driver.window_handles[tab_index])
        
        self.driver.get(url)

    def is_browser_alive(self):
        """Verifica si el navegador sigue activo"""
        try:
            return hasattr(self, 'driver') and self.driver.service.is_connectable()
        except:
            return False

    def wait_for_element(self, by: By, value: str, timeout: int = 10) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False
        
    def wait_for_visible(self, by: By, value: str, timeout: int = 10):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, value)))
        except TimeoutException:
            return False

    def wait_clickable(self, by: By, value: str, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value)))

    def send_keys(self, by: By, value: str, keys: str, clear: bool = True):
        element = self.wait_for_visible(by, value)
        if clear:
            element.clear()
        element.send_keys(keys)

    def safe_click(self, by: By, value: str, tab_index: int = 0):
        """Click seguro que previene apertura de nuevas ventanas en una pestaña específica"""
        try:
            # Cambiar a la pestaña correspondiente
            self.driver.switch_to.window(self.driver.window_handles[tab_index])

            element = self.wait_clickable(by, value)

            # Forzar scroll al elemento manualmente
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

            # Intentar hacer clic con JS sin propagar
            self.driver.execute_script("""
                arguments[0].addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                });
                arguments[0].click();
            """, element)
            return True
        except Exception as e:
            print(f"Error en safe_click: {str(e)}")
            return False

    def click(self, by: By, value: str, tab_index: int = 0) -> bool:
        """Método click compatible con modo headless."""
        intento = 0
        for intento in range(3):
            try:
                self.driver.switch_to.window(self.driver.window_handles[tab_index])
                element = self.wait_clickable(by, value)

                # Scroll seguro (compatible con headless)
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)

                # Intento con ActionChains + fallback a JavaScript
                try:
                    ActionChains(self.driver).move_to_element(element).pause(0.3).click().perform()
                except:
                    intentos = 0
                    while intentos < 3:
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            self.driver.execute_script("arguments[0].click();", element)
                            break
                        except:
                            intentos += 1
                            sleep(1)
                            
                return True  # Éxito

            except Exception as e:
                print(f"Intento {intento + 1} fallido: {str(e)}")
                
                if intento < 2:
                    sleep(1)

        return False  # Falló después de 3 intentos

    def wait_for_new_tab(self, old_tabs, timeout: int = 10):
        try:
            return WebDriverWait(self.driver, timeout).until(lambda d: len(d.window_handles) > len(old_tabs))
        except TimeoutException:
            return False

    def get_text(self, by: By, value: str, timeout: int = 5) -> int:
        """Extrae el texto visible de un elemento web.
        
        Args:
            by: Estrategia de localización (By.CSS_SELECTOR, By.XPATH, etc.)
            value: Valor del selector
            timeout: Tiempo máximo de espera (en segundos)
            
        Returns:
            Texto del elemento, o cadena vacía si no se encuentra.
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
            return element.text.strip()
        except TimeoutException:
            return ""
        
    def get_elements_attribute(self, by: By, value: str, attribute: str = "src", timeout: int = 5) -> List[str]:
        """Obtiene una lista única de valores de atributo o texto de elementos.
        
        Args:
            attribute: Puede ser "text" para obtener el texto visible, o cualquier atributo HTML como "src".
        """
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((by, value)))
                
                valores = []
                for el in elements:
                    try:
                        if attribute == "text":
                            # Obtener el texto visible del elemento
                            text_value = el.text.strip()
                            if text_value:
                                valores.append(text_value)
                        else:
                            # Obtener un atributo HTML normal
                            attr_value = el.get_attribute(attribute)
                            if attr_value:
                                valores.append(str(attr_value))
                    except Exception:
                        continue
                
                # Eliminar duplicados manteniendo el orden
                seen = set()
                unique_valores = [x for x in valores if not (x in seen or seen.add(x))]
                
                return unique_valores
                    
            except TimeoutException:
                pass  # Continuar al siguiente intento
            except Exception:
                pass  # Continuar al siguiente intento
            
            attempt += 1
            if attempt < max_attempts:
                sleep(1)  # Pequeña pausa entre intentos
        
        return []  # Retorna lista vacía después de 3 intentos fallidos
     
    def count_elements(self, by: By, value: str, timeout: int = 5) -> int:
        """Cuenta cuántos elementos coinciden con el selector dado.
        
        Args:
            by: Estrategia de localización (By.CSS_SELECTOR, By.XPATH, etc.)
            value: Valor del selector
            timeout: Tiempo máximo de espera (en segundos)
            
        Returns:
            Número de elementos encontrados que coinciden con el selector
        """
        try:
            elements = WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
            
            return len(elements)
        except TimeoutException:
            return 0

    def __del__(self):
        """Limpieza segura al destruir la instancia"""
        if hasattr(self, 'driver') and self.is_browser_alive():
            try:
                self.driver.quit()
            except:
                pass