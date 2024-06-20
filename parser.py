from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
import json


class Parser:
    def __init__(self, url: str) -> None:
        self.url = url
        # здесь храняться те блюда которые уже просмотрины
        self.clicked_cards = set()
        self.pars_data = {
            'photo': '',
            'price': '',
            'title': '',
            'description': ''
        }
    
        # Настройка драйвера Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Запуск в фоновом режиме, без отображения окна браузера
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.cookies = [{"name":"yandexuid","value":"384142161716910258"},{"name":"spravka","value":"dD0xNjg1NjEwOTQ3O2k9MmEwMDoxZmEyOjQxMzE6NTczODpkZjVkOjdlYjQ6OGNmOjg1OGM7RD1EMEYwRTZEQURBRjhEOTZDNDdCRTJFODc2RTUyMDBBQzE2MjY0MkQxOEMwMTNFNUIyM0M3MzE3Q0M5MkFDN0QwQUFEOUM0RDA5NkY4Q0JGRDt1PTE2ODU2MTA5NDc4MDU3OTQwODY7aD00NjVmZmY2NDk3NTA2MTc5Y2ZmMmJlZmE5NGE2NzA0YQ"},{"name":"amcuid","value":"1640817451717147532"},{"name":"is_gdpr","value":"0"},{"name":"is_gdpr_b","value":"COG2HhDp/wE"},{"name":"yuidss","value":"384142161716910258"},{"name":"yp","value":"2034180096.udn.cDpkZW4tMDkta2Fk"},{"name":"L","value":"dVNoAwFacF1LXlNtTFEJe1QEflFqQAlUNh0GQlt8SzMlVg"},{"name":"yandex_login","value":"den-09-kad"},{"name":"ys","value":"udn.cDpkZW4tMDkta2Fk#c_chck.3705171551"},{"name":"bh","value":"EkEiQ2hyb21pdW0iO3Y9IjEyNCIsICJHb29nbGUgQ2hyb21lIjt2PSIxMjQiLCAiTm90LUEuQnJhbmQiO3Y9Ijk5IhoFIng4NiIiDyIxMjQuMC42MzY3Ljc4IioCPzAyAiIiOgciTGludXgiQgciNi44LjkiSgQiNjQiUlsiQ2hyb21pdW0iO3Y9IjEyNC4wLjYzNjcuNzgiLCAiR29vZ2xlIENocm9tZSI7dj0iMTI0LjAuNjM2Ny43OCIsICJOb3QtQS5CcmFuZCI7dj0iOTkuMC4wLjAiWgI/MGCHiNCzBg"},{"name":"font_loaded","value":"YSv1"},{"name":"_yasc","value":"vnqyaO564XFRiW2EIya2islMdcV4Cpd+KOhYipjBKPkstAPv31539c5RxxNMCvW/CGg"},{"name":"eda_web","value":"{%22app%22:{%22analyticsSession%22:{%22id%22:%22lxnega9z-e5n4zdl6a3e-6n9taztbqf-cq4egpft4zv%22%2C%22start%22:1718896260%2C%22update%22:1718909288}%2C%22deliveryTime%22:null%2C%22themeVariantKey%22:%22light%22%2C%22xDeviceId%22:%22lxlwrtcf-bam6qv5dbog-x4dme4v1qsf-3wbmu89kavg%22%2C%22lastObtainedGps%22:{%22lat%22:38.883333%2C%22lon%22:-77%2C%22timestamp%22:1718824098445}%2C%22lat%22:57.147566445521214%2C%22lon%22:65.55251315305341}}"}]

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def scroll_down(self) -> None:
        """
        Прогрутить на один экран страницу и подождать 2 секунды чтобы прогрузились все элементы
        """
        scroll_height = self.driver.execute_script("return window.innerHeight")
        self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(2)  # Даем время на подгрузку новых элементов

    def check_card(self, card_id: str) -> bool:
        return card_id not in self.clicked_cards
    
    def get_visible_elements(self, locator: tuple) -> bool:
        return self.driver.find_elements(*locator)

    def close_panel(self) -> None:
        close = self.driver.find_element(By.CLASS_NAME, "DesktopUIButton_root.ModalCross_button.DesktopUIButton_simple.DesktopUIButton_sm")
        self.driver.execute_script("arguments[0].click();", close)

    def open_panel(self, card_id: str, card) -> None:
        self.clicked_cards.add(card_id)
        self.driver.execute_script("arguments[0].click();", card)

    def get_page(self) -> None:
        self.driver.get(self.url)
        
        for cookie in self.cookies:
            self.driver.add_cookie({
                'name': cookie['name'],
                'value': cookie['value'],
            })

        # Обновление страницы для применения куки
        self.driver.refresh()

        time.sleep(10)

    def get_data(self) -> None:
        title = self.driver.find_element(By.CLASS_NAME, "ProductFullCardName_cardName")
        description = self.driver.find_element(By.CLASS_NAME, "UiKitProductCardDescriptions_descriptionText")
        price = self.driver.find_element(By.CLASS_NAME, "UiKitCorePrice_price.UiKitCorePrice_xl.UiKitCorePrice_bold")
        try:
            photo = self.driver.find_element(By.CLASS_NAME, "SmartImage_containFitImg")
        except:
            photo = self.driver.find_element(By.CLASS_NAME, "SmartImage_coverFitImg")


        self.pars_data['title'] = title.text
        self.pars_data['photo'] = photo.get_attribute('src')
        self.pars_data['price'] = price.text
        self.pars_data['description'] = description.text

        print(self.pars_data)
        

    def page_end(self) -> bool:
        current_height = self.driver.execute_script("return document.documentElement.scrollTop + window.innerHeight")
        total_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        return current_height >= total_height

    def get_context(self) -> None:
        with open('context.txt', 'r') as file:
            context_list = file.readlines()

        try:
            if context_list[0].strip() == self.url:
                self.clicked_cards = set(context_list[1:])

            else:
                with open('context.txt', 'w') as file:
                    file.write(self.url + "\n")
        except:
            with open('context.txt', 'w') as file:
                file.write(self.url + "\n")


    def set_context(self, line: str) -> None:
        with open('context.txt', 'a') as file:
            file.write(line + "\n")


if __name__ == "__main__":
    url = "https://eda.yandex.ru/tumen/r/sushi_master?placeSlug=sushimastergor"
    pars = Parser(url)
    pars.get_context()
    pars.get_page()
    # locator по которому мы будем находить карты
    card_locator = (By.CLASS_NAME, "UiKitDesktopProductCard_fakeWrapper")
    while True:
        # Получаем видимые карточки
        visible_cards = pars.get_visible_elements(card_locator)

        # Флаг для отслеживания новых карточек
        new_card_found = False

        for card in visible_cards:
            # сохраняем катру в просмотренных картах
            card_id = card.get_attribute("aria-label")  # Используем уникальный атрибут, например id
            if pars.check_card(card_id):
                try:
                    pars.set_context(card_id)
                    pars.open_panel(card_id, card)
                    time.sleep(1)
                    pars.get_data()
                    pars.close_panel()
                except:
                    continue

                new_card_found = True

        if not new_card_found:
            # Прокручиваем страницу вниз
            pars.scroll_down()
            
            # Проверяем, достигли ли конца страницы
            if pars.page_end():
                break  # Если достигли конца страницы, выходим из цикла