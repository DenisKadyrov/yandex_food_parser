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
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def scroll_down(self):
        scroll_height = self.driver.execute_script("return window.innerHeight")
        self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(2)  # Даем время на подгрузку новых элементов

    def check_card(self, card_id) -> bool:
        return card_id not in self.clicked_cards
    
    def get_visible_elements(self, locator):
        return self.driver.find_elements(*locator)

    def close_panel(self):
        close = self.driver.find_element(By.CLASS_NAME, "DesktopUIButton_root.ModalCross_button.DesktopUIButton_simple.DesktopUIButton_sm")
        self.driver.execute_script("arguments[0].click();", close)

    def open_panel(self, card_id, card):
        self.clicked_cards.add(card_id)
        self.driver.execute_script("arguments[0].click();", card)

    def get_page(self) -> None:
        self.driver.get(self.url)
        time.sleep(10)

    def get_data(self) -> None:
        title = self.driver.find_element(By.CLASS_NAME, "ProductFullCardName_cardName")
        description = self.driver.find_element(By.CLASS_NAME, "UiKitProductCardDescriptions_descriptionText")
        price = self.driver.find_element(By.CLASS_NAME, "UiKitCorePrice_price")
        photo = self.driver.find_element(By.CLASS_NAME, "SmartImage_containFitImg")

        self.pars_data['title'] = title.text
        self.pars_data['photo'] = photo.get_attribute('src')
        self.pars_data['price'] = price.text
        self.pars_data['description'] = description.text

        print(self.pars_data)
        

    def page_end(self) -> bool:
        current_height = self.driver.execute_script("return document.documentElement.scrollTop + window.innerHeight")
        total_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        return current_height >= total_height

    def get_context(self):
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


    def set_context(self, line):
        with open('context.txt', 'a') as file:
            file.write(line + "\n")


if __name__ == "__main__":
    url = "https://eda.yandex.ru/tumen/r/burger_king_ynrku?placeSlug=burger_king_qjbzs"
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