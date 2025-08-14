from google import genai
from controller.Config import Config

class CaptchaExtractor(Config):
    def __init__(self) -> None:
        """Constructor optimizado que usa la instancia singleton del navegador"""
        super().__init__()

    def extract_with_gemini(self, image_data: str) -> dict:
        """Extrae el texto de un captcha usando Gemini"""

        client = genai.Client(api_key=self.key_gemini)

        prompt = """
        Eres un extractor de texto especializado en captchas.  
        Responde únicamente con los caracteres del captcha, sin espacios ni saltos de línea, 
        en el mismo orden en que aparecen, respetando mayúsculas y minúsculas.

        Esquema de salida:
        <string>

        Reglas:
        - "captcha" debe contener exactamente los caracteres visibles en la imagen, en el mismo orden y respetando mayúsculas y minúsculas.
        - No corrijas, interpretes ni sustituyas caracteres aunque parezcan similares (por ejemplo, no cambiar '0' por 'O').
        - No incluyas espacios adicionales, saltos de línea ni otro tipo de caracteres que no aparezcan en la imagen.
        - No incluyas comentarios, explicaciones ni texto extra fuera del string.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {"role": "user", "parts": [
                    {"text": prompt},
                    {"inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }}
                ]}
            ]
        )

        try:
            return "".join(response.text.strip().split())
        except:
            raise ValueError("Gemini no devolvió un texto válido")
