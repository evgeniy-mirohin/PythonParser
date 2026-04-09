import asyncio
from playwright.async_api import async_playwright
import time

async def run():
    async with async_playwright() as p:
        # Используем Edge с отключением признаков автоматизации
        browser = await p.chromium.launch(
            headless=False, 
            channel="msedge",
            args=["--disable-blink-features=AutomationControlled"] 
        )
        
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            await page.goto("https://avito.ru", wait_until="networkidle")

            # Подтверждаем город
            confirm = page.locator('button[data-marker="location/confirm"]')
            if await confirm.is_visible(timeout=5000):
                await confirm.click()

            # Ввод текста
            search_input = page.locator('input[placeholder="Поиск по объявлениям"]')
            await search_input.fill("ноутбук")
            
            # Нажимаем на саму кнопку поиска вместо Enter (это надежнее)
            search_button = page.locator('button[data-marker="search-form/submit-button"]')
            await search_button.click()
            print("Клик по кнопке поиска выполнен")

            # Ждем появления результатов с большим таймаутом
            # Если тут упадет — посмотрите в окно браузера, там наверняка капча
            await page.wait_for_selector('[data-marker="catalog-serp"]', timeout=60000)
            
            # ... сбор данных ...
 # 5. Собираем все карточки товаров
            items = page.locator('[data-marker="item"]')
            count = await items.count()
            print(f"Найдено объявлений: {count}")

            results = []

            for i in range(count):
                item = items.nth(i)
                try:
                    # Извлекаем название
                    title = await item.locator('[data-marker="item-title"]').get_attribute("title")
                    
                    # Извлекаем цену (берем атрибут content из мета-тега — это самое надежное)
                    # Если нужен текст с символом рубля, используйте .inner_text() на [data-marker="item-price"]
                    price_element = item.locator('meta[itemprop="price"]')
                    price = await price_element.get_attribute("content")
                    
                    if title and price:
                        results.append({
                            "title": title,
                            "price": price
                        })
                        print(f"{i+1}. {title} — {price} руб.")
                except Exception:
                    continue # Пропускаем, если карточка пустая (например, реклама)

            print(f"\nИтого собрано цен: {len(results)}")
        except Exception as e:
            print(f"Ошибка: {e}")
            # Делаем скриншот ДО того, как закроется браузер
            try:
                await page.screenshot(path="debug_playwright.png")
                print("Скриншот сохранен в debug_playwright.png")
            except:
                pass 
        finally:
            # Даем время посмотреть глазами перед закрытием
            await page.wait_for_timeout(5000)
            await browser.close()


asyncio.run(run())
