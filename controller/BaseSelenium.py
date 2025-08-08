from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium import webdriver # type: ignore
from selenium.common.exceptions import TimeoutException, WebDriverException # type: ignore
from selenium.webdriver.firefox.service import Service # type: ignore
from selenium.webdriver.firefox.options import Options # type: ignore
from controller.utils.Helpers import Helpers
from selenium.webdriver.common.keys import Keys
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

        service = Service(executable_path=driver_path, log_path="geckodriver.log")

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

    def send_keys(self, by: By, value: str, keys=None, clear: bool = True, special_key=None, delay: float = 0.2):
        """
        Envía texto y/o teclas especiales a un elemento, manejando el foco dinámico.
        
        Args:
            by: Estrategia de localización
            value: Valor del selector
            keys: Texto a enviar (str) o None
            clear: Si debe limpiar el campo primero
            special_key: Tecla especial (str) o lista de teclas (list)
                        Las teclas se aplican al elemento con foco actual
            delay: Tiempo entre teclas en segundos (default: 0.2)
        """
        
        # Mapeo completo de teclas
        key_mapping = {
            "ENTER": Keys.RETURN,
            "TAB": Keys.TAB,
            "ESC": Keys.ESCAPE,
            "SPACE": Keys.SPACE,
            "BACKSPACE": Keys.BACKSPACE,
            "ARROWUP": Keys.ARROW_UP,
            "ARROWDOWN": Keys.ARROW_DOWN,
            "ARROWLEFT": Keys.ARROW_LEFT,
            "ARROWRIGHT": Keys.ARROW_RIGHT,
            "F1": Keys.F1,
            "F2": Keys.F2,
        }
        
        # Paso 1: Manejar elemento inicial (si se especificó)
        if by and value:
            element = self.wait_for_visible(by, value)
            if clear:
                element.clear()
            
            if keys:
                element.send_keys(keys)
                sleep(delay)
        
        # Paso 2: Procesar teclas especiales (usando foco actual)
        if special_key:
            keys_sequence = [special_key] if isinstance(special_key, str) else special_key
            
            for i, key in enumerate(keys_sequence):
                key_value = key_mapping.get(key.upper())
                if not key_value:
                    raise ValueError(f"Tecla no soportada: {key}")
                
                # Para la primera tecla: usar elemento inicial (si existe)
                if i == 0 and by and value:
                    element.send_keys(key_value)
                else:
                    active_element = self.driver.switch_to.active_element
                    try:
                        active_element.send_keys(key_value)
                    except:
                        # Fallback para elementos no interactivos
                        self.driver.execute_script(f"""
                            var evt = new KeyboardEvent('keydown', {{key: '{key_value}'}});
                            arguments[0].dispatchEvent(evt);
                        """, active_element)
                
                sleep(delay)

    def handle_link_element(self, by: By, value: str, action: str = "click", special_key=None, tab_index: int = 0):
        """
        Maneja elementos de tipo enlace (<a>) de forma segura, con múltiples opciones de interacción.
        
        Args:
            by: Estrategia de localización (By.XPATH, By.CSS_SELECTOR, etc.)
            value: Valor del selector
            action: Acción a realizar ("click", "verify", "get_text", "get_href")
            special_key: Tecla especial a enviar (opcional)
            tab_index: Índice de la pestaña donde buscar el elemento
            
        Returns:
            - Para action="verify": True si el elemento existe y es visible, False en caso contrario
            - Para action="click": True si se pudo interactuar con el elemento, False en caso contrario
            - Para action="get_text": El texto del enlace o None si no se encontró
            - Para action="get_href": El valor del atributo href o None si no se encontró
        """
        try:
            # Cambiar a la pestaña correcta
            self.driver.switch_to.window(self.driver.window_handles[tab_index])
            
            # Esperar a que el elemento esté presente
            element = self.wait_for_visible(by, value)
            
            if not element:
                return False if action != "get_text" and action != "get_href" else None
            
            # Verificar que sea un elemento <a>
            tag_name = element.tag_name.lower()
            if tag_name != "a":
                print(f"Advertencia: El elemento encontrado no es un enlace (<a>), es: {tag_name}")
            
            # Realizar la acción solicitada
            if action == "verify":
                return element.is_displayed()
                
            elif action == "click":
                try:
                    # Intento con JavaScript primero (más robusto)
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as js_error:
                    print(f"Intento con JavaScript falló: {js_error}. Intentando con ActionChains...")
                    try:
                        ActionChains(self.driver).move_to_element(element).click().perform()
                        return True
                    except Exception as ac_error:
                        print(f"Error al hacer clic en el elemento: {ac_error}")
                        return False
                        
            elif action == "get_text":
                try:
                    return element.text.strip()
                except:
                    return None
                    
            elif action == "get_href":
                try:
                    return element.get_attribute("href")
                except:
                    return None
                    
            # Manejo de teclas especiales si se especificaron
            if special_key:
                key_actions = {
                    "ENTER": lambda: element.send_keys(Keys.RETURN),
                    "SPACE": lambda: self.driver.execute_script("arguments[0].click();", element),
                }
                
                for key in ([special_key] if isinstance(special_key, str) else special_key):
                    action_func = key_actions.get(key.upper())
                    if action_func:
                        try:
                            action_func()
                            sleep(0.3)
                        except Exception as key_error:
                            print(f"Error al ejecutar tecla {key}: {key_error}")
                            continue
            
            return True
            
        except Exception as e:
            print(f"Error en handle_link_element: {str(e)}")
            return False if action != "get_text" and action != "get_href" else None

    def send_keys_link(self, by: By, value: str, special_key=None):
        """
        Versión especializada para enlaces (<a> tags)
        """
        element = self.wait_for_visible(by, value)
        
        # 1. Scroll y focus
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        element.click()
        sleep(0.3)
        
        # 2. Manejo de teclas
        if special_key:
            key_actions = {
                "ENTER": lambda: element.send_keys(Keys.RETURN),
                "SPACE": lambda: self.driver.execute_script("arguments[0].click();", element),
            }
            
            for key in ([special_key] if isinstance(special_key, str) else special_key):
                key_actions.get(key.upper(), lambda: None)()
                sleep(0.3)

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
    
    def click_metode(self, by: By, value: str, metode: str = "oamSubmitForm"):
        element = self.driver.find_element(by, value)
                            
        # Ejecutar directamente el JavaScript onclick
        self.driver.execute_script(
            "arguments[0].onclick();", 
            element
        )
        
        # Alternativa: llamar a la función JS directamente
        form_id = element.get_attribute("onclick").split("'")[1]
        form_name = element.get_attribute("onclick").split("'")[3]
        self.driver.execute_script(
            f"{metode}('{form_id}','{form_name}');"
        )

    def wait_for_new_tab(self, old_tabs, timeout: int = 10):
        try:
            return WebDriverWait(self.driver, timeout).until(lambda d: len(d.window_handles) > len(old_tabs))
        except TimeoutException:
            return False
        
    def switch_to_new_tab(self, element_locator: str, close_current_tab: bool = False) -> str:
        """Abre una nueva pestaña haciendo clic en un elemento y cambia el foco a ella.
        
        Args:
            element_locator: Locator XPath del elemento que al hacer clic abre nueva pestaña
            close_current_tab: Si es True, cierra la pestaña original después de cambiar
            
        Returns:
            str: El handle de la pestaña original (útil para volver luego)
            
        Raises:
            TimeoutException: Si no aparece una nueva pestaña en el tiempo esperado
            NoSuchElementException: Si no se encuentra el elemento a hacer clic
        """
        original_window = self.driver.current_window_handle
        original_tabs = set(self.driver.window_handles)
        
        # Hacer clic en el elemento que abre la nueva pestaña
        self.click(By.XPATH, element_locator)
        
        # Esperar y cambiar a la nueva pestaña
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.window_handles) > len(original_tabs))
            
            new_tab = next(tab for tab in self.driver.window_handles 
                        if tab not in original_tabs)
            self.driver.switch_to.window(new_tab)
            
            if close_current_tab:
                self.driver.switch_to.window(original_window)
                self.driver.close()
                self.driver.switch_to.window(new_tab)
                
            return original_window
            
        except TimeoutException:
            raise TimeoutException("No se abrió una nueva pestaña después de hacer clic")

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
    
    def switch_to_frame(self, frame_reference, timeout=10):
        """
        Cambia al iframe especificado de manera segura.
        
        Args:
            frame_reference: Puede ser:
                - Un WebElement (obtenido con find_element)
                - Un índice numérico (0-based)
                - Un nombre o ID del frame (string)
            timeout: Tiempo máximo de espera
        """
        try:
            if isinstance(frame_reference, str):
                # Si es string, asumimos que es ID/name
                WebDriverWait(self.driver, timeout).until(
                    EC.frame_to_be_available_and_switch_to_it(frame_reference)
                )
            elif isinstance(frame_reference, int):
                # Si es entero, asumimos que es índice
                self.driver.switch_to.frame(frame_reference)
            else:
                # Si es WebElement
                WebDriverWait(self.driver, timeout).until(
                    EC.frame_to_be_available_and_switch_to_it(frame_reference)
                )
            return True
        except Exception as e:
            print(f"Error al cambiar al frame: {str(e)}")
            self.driver.switch_to.default_content()
            return False
     
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