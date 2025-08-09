from controller.BaseSelenium import BaseSelenium
from dotenv import load_dotenv
from os import getenv

class Config(BaseSelenium):
    """
    Clase encargada de de generar variables globales desde .env
    """

    def __init__(self) -> None:
        """Constructor de la clase. Hereda de BaseSelenium e inicializa el navegador."""
        load_dotenv()
        super().__init__()
        self.url_home = self.helper.get_value("sena", "url_home")
        self.url_login = self.helper.get_value("sena", "url_login")
        self.url_certificado = self.helper.get_value("sena", "url_certificado")
        self.username  = getenv("USER")
        self.password  = getenv("PASSWD")