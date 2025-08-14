from controller.BaseSelenium import BaseSelenium
from dotenv import load_dotenv

class Config(BaseSelenium):
    """
    Clase encargada de de generar variables globales desde .env
    """

    def __init__(self) -> None:
        """Constructor de la clase. Hereda de BaseSelenium e inicializa el navegador."""
        load_dotenv()
        super().__init__()
        self.key_gemini = self.helper.get_value("KEY")
        self.url_home = self.helper.get_value("sena", "url_home")
        self.url_login = self.helper.get_value("sena", "url_login")
        self.username  = self.helper.get_value("sena", ["login", "USER"])
        self.password  = self.helper.get_value("sena", ["login", "PASSWD"])
        self.password  = self.helper.get_value("sena", ["login", "PASSWD"])
        self.user_email = self.helper.get_value("email")
        self.user_pass = self.helper.get_value("passwd")
        base = self.helper.get_value("sena", ["url_certificado", "base"])
        self.url_portal_certificado = base + "." + self.helper.get_value("sena", ["url_certificado", "constulta"])
        self.url_certificado_descarga = base + "." + self.helper.get_value("sena", ["url_certificado", "descarga"])