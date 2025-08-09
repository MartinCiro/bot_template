from controller.Config import Config
from selenium.webdriver.common.by import By

class Browse_web(Config):
    def __init__(self) -> None:
        """Constructor optimizado que usa la instancia singleton del navegador"""
        super().__init__()
        
        
    def _navigate_to_aprendiz(self):
        # Navegar hasta aprendiz
        self.send_keys(
            By.XPATH, 
            "//a[@id='Salirform:cmdLogOut']", 
            None, 
            clear=False, 
            special_key=["TAB", "ENTER", "ARROWUP", "ENTER"],
            delay=0.3
        )

    def _navigate_to_certified(self):
        self.handle_link_element(
            By.XPATH, 
            "//span[contains(normalize-space(text()), 'Certificación')]/ancestor::a",
            action="click",
            special_key="ENTER"
        )

        self.handle_link_element(
            By.XPATH, 
            "//span[contains(normalize-space(text()), 'Certificación')]/ancestor::a/following-sibling::ul//a",
            action="click",
            special_key="ENTER"
        )

        self.handle_link_element(
            By.XPATH, 
            "//a[contains(text(), 'Consultar Constancias')]",
            action="click",
            special_key="ENTER"
        )
    
    def _select_certified(self):
        xpath_locator = "//span[contains(., 'TECNÓLOGO EN ANALISIS')]/ancestor::tr//a[contains(@id, 'clConsultaCertificadosgenerados')]"
        if self.switch_to_frame("contenido"):
            try:
                if self.wait_for_element(By.XPATH, xpath_locator, timeout=5):
                    self.click_metode(By.XPATH, xpath_locator)
                    return print("Encontrado" if self.wait_for_element(By.XPATH, "//h2[contains(., 'Estado del Certificado')]/following-sibling::table//span[contains(text(), 'CERTIFICADO')]", timeout=5) else "No encontrado")
            finally:
                self.driver.switch_to.default_content()
    
    """ def _brose_download_certified(self):
        # 1053872476
        btn_consult="//input[@name='CONSULTAR']"
        if not self.wait_for_element(By.XPATH, btn_consult, timeout=2):
            return False
        
        self.open_url(self.url_certificado) """

    def navigate_certified(self):
        self._navigate_to_aprendiz()
        self._navigate_to_certified()
        self._select_certified()