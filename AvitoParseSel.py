from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url = "https://avito.ru"
s = Service(executable_path="D:\\python\\progect\\Selenium\\edgedriver\\146.0.3856.109\\msedgedriver.exe")

# --- НАСТРОЙКИ МАСКИРОВКИ ---
options = webdriver.EdgeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0")

driver = webdriver.Edge(service=s, options=options)

# Убираем флаг webdriver из свойств браузера
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})

try:
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)

    # 1. Нажимаем "Да" в окне выбора города
    try:
        confirm_city = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-marker="location/tooltip-agree"]')))
        confirm_city.click()
        print("Город подтвержден")
    except Exception:
        print("Окно выбора города не появилось или не найдено")

    # 2. Находим поле поиска по placeholder
    print("Ищу поле ввода...")
    text_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="Поиск по объявлениям"]')))
    
    text_box.click()
    text_box.send_keys("ноутбук")
    print("Текст введен")
    
    # 3. Нажимаем ENTER для поиска
    text_box.send_keys(Keys.ENTER)
    print("Поиск запущен")

        # 4. Ждем загрузки результатов (ждем появления контейнера с объявлениями)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="catalog-serp"]')))
    time.sleep(2) # Небольшая пауза для прогрузки цен

    # 5. Собираем названия и цены
    items = driver.find_elements(By.CSS_SELECTOR, 'div[data-marker="item"]')

    print(f"\nНайдено объявлений: {len(items)}")
    print("-" * 30)

    for item in items:
        try:
            # 1. Название машины (из атрибута title у ссылки)
            title_element = item.find_element(By.CSS_SELECTOR, 'a[data-marker="item-title"]')
            title = title_element.get_attribute("title")

            # 2. Цена (из мета-тега внутри)
            price_element = item.find_element(By.CSS_SELECTOR, 'meta[itemprop="price"]')
            price = price_element.get_attribute("content")

            # 3. Ссылка на объявление
            link = title_element.get_attribute("href")

            print(f"Авто: {title}")
            print(f"Цена: {price} руб.")
            print(f"Ссылка: {link}")
            print("-" * 20)

        except Exception:
            continue

    print("-" * 30)

except Exception as ex:
    driver.save_screenshot("error_step.png")
    print(f"Ошибка: {ex}")


finally:
    driver.quit()
