from controller.BaseSelenium import BaseSelenium
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from controller.Login import LoginDropi
from controller.CLIPEmbedder import CLIPEmbedder
from controller.FAISSIndex import FAISSIndex
from controller.Peticiones import Peticiones
from time import sleep
from re import sub, split

login_page = LoginDropi()
clip = CLIPEmbedder()
faiss = FAISSIndex()

class Data_Products(BaseSelenium):
    def __init__(self) -> None:
        """Constructor optimizado que usa la instancia singleton del navegador"""
        super().__init__()
        self.url_catalogo = self.helper.get_value("dropi", "url_catalogo")
        self.url_login = self.helper.get_value("dropi", "url_login")
        self.multiselect_wait = "//p-multiselect[contains(@class, 'provider-select__select')]"
        self._navigate_to_catalog()
        self.current_url = self.driver.current_url

    def _navigate_to_catalog(self):
        """Garantiza que estamos en la URL correcta al iniciar"""
        if not self.driver.current_url == self.url_catalogo:
            self._cx_catalogo()
    
    def _cx_catalogo(self):
        login_page.login()

    def _get_icon_card(self, card_n):
        base = "//button[@class='card-actions']/preceding-sibling::div[1]//"
        price = f"({base}div[contains(@class, 'price-provider')])[{card_n}]"
        title = f"({base}h3[contains(@class, 'tittle-product')])[{card_n}]"
        proveedor = f"({base}span[contains(@class, 'provider-name')])[{card_n}]"
        return price, title, proveedor

    def _navigation(self, btn_xpath_apply, attempts, card):
        """ multiselect_xpath = "//div[contains(@class, 'p-multiselect-label')]/text()[normalize-space(.)='Proveedor']/ancestor::div/following-sibling::div/chevrondownicon"
        premium_xpath = "//li[@aria-label='Premium']"
        verified_xpath = "//li[@aria-label='Verificado']"

        
        price, _, _ = self._get_icon_card(card)
        
        if self.wait_for_element(By.XPATH, price, timeout=15):
            attempts += 1
            self._navigate_to_catalog()
        
        # 1. Abrir multiselect
        self.safe_click(By.XPATH, multiselect_xpath)
        self.click(By.XPATH, multiselect_xpath)
        self.safe_click(By.XPATH, self.multiselect_wait)
        self.click(By.XPATH, self.multiselect_wait)

        # 2. Seleccionar opciones
        self.click(By.XPATH, premium_xpath)
        self.click(By.XPATH, verified_xpath)

        self.click(By.XPATH, btn_xpath_apply) """
        return True
    
    def _tabs(self, click):
        old_tabs = self.driver.window_handles
        self.click(By.XPATH, click)
        self.wait_for_new_tab(old_tabs)
        new_tab = next(tab for tab in self.driver.window_handles if tab not in old_tabs)
        self.driver.switch_to.window(new_tab)
        if not self.wait_for_element(By.XPATH, self.multiselect_wait , timeout=15):
            self._cx_catalogo()
        return old_tabs

    def _process_tab(self, i, sub_page=False):
        click_icon, title_xpath, proveedor = self._get_icon_card(i)
        if not self.wait_for_element(By.XPATH, title_xpath, timeout=3):
            self._cx_catalogo()

        title = self.get_text(By.XPATH, title_xpath)
        old_tabs = self._tabs(click_icon) if sub_page else self._tabs(proveedor)
        
        tab_title = self.get_text(By.XPATH, "//h2")
        self.current_url = self.driver.current_url
        
        
        return tab_title, title, old_tabs
    
    def clean_val(self, valor):
        limpio = sub(r"[^0-9,]", "", valor)  # Elimina todo excepto dígitos y coma
        return limpio
    
    def _data_constructor(self, lista, time, sub_page=False):
        fallo_total = []
        iterable  = range(1, lista) if isinstance(lista, int) else lista
        image_xpath = "//div[@class='p-galleria-content']//img"
        details_xpath = "//*[@header='Detalles']/div"
        contact_xpath = "//div[starts-with(@class, 'contact')]/a"
        provi_name_xpath = "//div[@class='provider_name']/h3"
        provi_price_xpath = "//div[@class='price-providers']//currency"
        provi_price_s_xpath = "//div[@class='price-suggested']//currency"
        category_xpath = "//div[@class='chips-container']"
        stock_xpath = "//section[@class='product_info_bottom']//span[@class='in-stock quantity']"

        # si provi_price es nullo debe traer las tallas
        base_list_talla_xpath = "//thead/following-sibling::tbody//td[#reem]//currency"
        provi_price_list_xpath = base_list_talla_xpath.replace('#reem', str(4))
        provi_price_s_list_xpath = base_list_talla_xpath.replace('#reem', str(5))

        stock_list_xpath = "//th[normalize-space()='Existencia']/ancestor::thead/following-sibling::tbody//span[contains(@class, 'quantity')]"
        talla_list_xpath = "//th[normalize-space()='Description']/ancestor::thead/following-sibling::tbody//td[2]/span"

        for i in iterable:
            max_attempts = 3
            attempt = 0
            success = False
            while attempt < max_attempts and not success:
                try:
                    tab_title, expected_title, old_tabs = self._process_tab(i, sub_page)
                    
                    if tab_title == expected_title:
                        data = {
                            "existing": False
                        }
                        # Armar el json aqui
                        try :
                            intentos_image = 0
                            images = []
                            id_faiss_list = []
                            details = self.get_text(By.XPATH, details_xpath)
                            contact = self.get_text(By.XPATH, contact_xpath)
                            provi_name = self.get_text(By.XPATH, provi_name_xpath)
                            tallas = self.get_elements_attribute(By.XPATH, talla_list_xpath, "text")
                            count_tallas = self.count_elements(By.XPATH, talla_list_xpath)
                            if count_tallas > 0:
                                tallas = [sub(r"^Talla:\s*", "", t) for t in tallas]
                                stock_list = self.get_elements_attribute(By.XPATH, stock_list_xpath, "text")
                                provi_price = self.get_elements_attribute(By.XPATH, provi_price_list_xpath, "text")
                                provi_price_s = self.get_elements_attribute(By.XPATH, provi_price_s_list_xpath, "text")
                            else:
                                stock_list = [self.get_text(By.XPATH, stock_xpath)]
                                provi_price = [self.get_text(By.XPATH, provi_price_xpath)]
                                provi_price_s = [self.get_text(By.XPATH, provi_price_s_xpath)]
                            
                            category = self.get_text(By.XPATH, category_xpath)
                            category = split(r'\n', category)
                            if category[0] == '':
                                category[0] = "Otros"

                            if provi_price_s[0] == '':
                                self.helper.save_json(f"errors.json", {"error": f"No se encontraron precios en la página: {self.current_url }"}, append=True)
                                continue

                            provi_price_cl = [self.clean_val(v) for v in provi_price]
                            provi_price_s_cl = [self.clean_val(v) for v in provi_price_s]

                            while intentos_image < 3:
                                try:
                                    images = self.get_elements_attribute(By.XPATH, image_xpath)
                                    if len(images) > 0:
                                        break  
                                except Exception as e:
                                    print(f"Error en el intento {intentos_image + 1}: {e}")
                                intentos_image += 1

                            if len(images) == 0:
                                fallo_total.append(i)
                                continue
                            
                            for img_url in images:
                                try:
                                    _, faiss_emb = clip.get_embedding_from_image_url(img_url)
                                    
                                    # Verificar si ya existe
                                    existing_id = faiss.get_existing_id(faiss_emb, 0.2)
                                    if existing_id is not None:
                                        id_faiss_list.append(existing_id)
                                        data["existing"] = True
                                    else:
                                        # Añadir nuevo embedding
                                        new_id = faiss.add_embeddings(faiss_emb)[0]
                                        faiss.save_index()
                                        id_faiss_list.append(new_id)
                                        
                                except Exception as e:
                                    print(f"Error al procesar imagen {img_url}: {e}")
                                    id_faiss_list.append(0)
                            
                        except Exception as e:
                            self.driver.close()  # Cerramos inmediatamente la pestaña nueva
                            self.driver.switch_to.window(old_tabs[0]) 
                            continue

                        data = {
                            "nombre": expected_title,
                            "descripcion": details,
                            "categoria": category,
                            "origen": "Dropi",
                            "proveedor": provi_name,
                            "contacto": contact,
                            "id_faiss": [int(id_) for id_ in id_faiss_list],
                            "url_img": images,
                            "existing": data["existing"],
                            "precios": [
                                {
                                    "valor": valor,
                                    "precio_sugerido": sugerido,
                                    "stock": stock,
                                    **({"talla": tallas[i]} if tallas else {})
                                }
                                for i, (valor, sugerido, stock) in enumerate(zip(provi_price_cl, provi_price_s_cl, stock_list))
                            ]
                        }
                        success = True
                        try:
                            response = Peticiones().carga_data_api(data)
                            print(f"✅ Datos enviados a la API: {response}")
                        except Exception as e:
                            print(f"Error al enviar datos a la base de datos: {e}")
                    else:
                        attempt += 1
                        if not self.wait_for_element(By.XPATH, self.multiselect_wait , timeout=15):
                            self._cx_catalogo()
                        sleep(time)

                    self.driver.close()  # Cerramos inmediatamente la pestaña nueva
                    self.driver.switch_to.window(old_tabs[0]) 
                except Exception as e:
                    attempt += 1
                    print(f"❌ Error en intento {attempt}: {str(e)}")
                    if not self.wait_for_element(By.XPATH, self.multiselect_wait, timeout=45):
                        self._navigate_to_catalog()
                    # Limpieza de emergencia si hay fallos
                    if len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        self.driver.close()
                    if len(self.driver.window_handles) > 0:
                        self.driver.switch_to.window(self.driver.window_handles[0])

            if not success:
                print(f"❌ Fallo definitivo en Tabla {i}")
                fallo_total.append(i)
                self.helper.save_json(f"{i}.json", {f"url: {self.current_url}"}, append=True)

        return fallo_total

    def data_products(self, time=3):
        """Versión mejorada con manejo de errores específicos"""
        try:
            self._navigate_to_catalog()

            card_actual = 40

            # Configurar selectores
            btn_xpath_apply = "//button[contains(text(), 'Aplicar filtros')]"

            if not self.wait_for_element(By.XPATH, self.multiselect_wait, timeout=45):
                self._navigate_to_catalog()

            attempts = 0
            
            while attempts < 3:
                if not self._navigation(btn_xpath_apply, attempts, card_actual):
                    attempts += 1
                    continue

                # 3. Verificar éxito
                if self.wait_for_element(By.XPATH, btn_xpath_apply):
                    sub_attempts = 0
                    while sub_attempts < 3:
                        price, _, _  = self._get_icon_card(card_actual)
                        if self.wait_for_element(By.XPATH, price):
                            card_actual = "."
                            count_card_icon, _, proveedor_xpath  = self._get_icon_card(card_actual)
                            limit = self.count_elements(By.XPATH, count_card_icon)

                            intentos_data = 0
                            while intentos_data < 3:
                                fallos = self._data_constructor(limit, time, sub_page=True)
                                if len(fallos) == 0:
                                    return True
                                else:
                                    # Si hay fallos, intenta reprocesarlos
                                    self._data_constructor(fallos, time, sub_page=True)
                                    intentos_data += 1

                            
                        sub_attempts += 1
                    print("❌ No se encontraron elementos de productos después de aplicar los filtros.")
                    return False
                attempts += 1

            print("❌ No se logró capturar la información de productos después de 3 intentos.")
            return False

        except TimeoutException:
            print("⚠️ Tiempo de espera agotado al buscar elementos")
            self.driver.save_screenshot("timeout_error.png")
            return False
            
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            self.driver.save_screenshot("unexpected_error.png")
            return False