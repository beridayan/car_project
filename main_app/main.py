from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

# פתח דפדפן (כאן כרום)
# עבור לאתר
def clean_price(price_str):
    # מסיר את כל התווים פרט למספרים
    return int(''.join(filter(str.isdigit, price_str)))
def get_car_price(car_name: str, car_year: str,marketing :str):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


    try:
        driver.get("https://www.carzone.co.il/")

        # ממתין לתיבת החיפוש
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"].css-18m03lx'))
        )

        # מזין את שם הרכב והשנה
        search_input.send_keys(f"{car_name} {marketing} {car_year} ")
        search_input.send_keys(Keys.RETURN)

        # ממתין למחיר להופיע
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.css-527czf.enfd39o2'))
        )

        price = price_element.text.strip()
        return price

    except Exception as e:
        return f"0"

    finally:
        driver.quit()

def percentage_change(a, b):
    try:
        return ((a - b) / b) * 100
    except ZeroDivisionError:
        return float('inf')  # or 0, depending on your preference


from yad2_scraper import fetch_vehicle_category

category = fetch_vehicle_category(
    vehicle_category="cars",
    page=1,
     price_range=(10000, 45000),
    year_range=(2010, 2023)
)
category.load_next_data()

cars = category.get_tags()
good_prices = []
for car in cars:
    name = getattr(car, 'model', 'No name')
    year = getattr(car, 'year', 'No year')
    price = getattr(car, 'price_string', 'No price')
    hand = getattr(car, 'hand', 'No hand')
    link = getattr(car, 'relative_link', None)
    marketing = getattr(car, 'marketing_text', None)
    f_marketing =  " ".join(str(marketing).split(' ')[2:3])
    print(f_marketing)
    mehiron = get_car_price(name,year,f_marketing)
    if mehiron != None:
        num = percentage_change(int(clean_price(mehiron)), int(clean_price(price)))

        if num > 20:
            if(link != None and price != None):
                print("https://www.yad2.co.il/vehicles/"+link)
                print(f"og price is {price} and mehiron price {mehiron}")
                to_save = "https://www.yad2.co.il/vehicles/"+link+f" \n og price is {price} and mehiron price {mehiron}"
                good_prices.append(to_save)
                print(good_prices)

        else:
            print('change is less then 30 ' + str(num))
            print(f"og price is {price} and mehiron price {mehiron}")
