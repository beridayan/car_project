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
def carzone(car_name: str, car_year: str,marketing :str):
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


    try:
        driver.get("https://www.carzone.co.il/")

        # ממתין לתיבת החיפוש
        search_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"].css-18m03lx'))
        )

        # מזין את שם הרכב והשנה
        search_input.send_keys(f"{car_name} {car_year} ")
        time.sleep(0.15)
        search_input.send_keys(Keys.RETURN)

        # ממתין למחיר להופיע
        price_element = WebDriverWait(driver, 2).until(
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
    

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_list_email(sender_email: str, receiver_email: str, app_password: str, subject: str, item_list: list):
    """
    Sends a list of items as an email.

    Args:
        sender_email (str): Your Gmail address.
        receiver_email (str): Recipient's email address (can be the same as sender).
        app_password (str): Gmail App Password (not your Gmail password).
        subject (str): Subject line of the email.
        item_list (list): The list of items to send.
    """
    # Email body (as plain text)
    body = "Here is the list:\n\n" + "\n".join(str(item) for item in item_list)

    # Set up the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:", e)

def send_str_email(sender_email: str, receiver_email: str, app_password: str, subject: str, item_list: list):
    """
    Sends a list of items as an email.

    Args:
        sender_email (str): Your Gmail address.
        receiver_email (str): Recipient's email address (can be the same as sender).
        app_password (str): Gmail App Password (not your Gmail password).
        subject (str): Subject line of the email.
        item_list (list): The list of items to send.
    """
    # Email body (as plain text)
    body = "Here is the list:\n\n" + "\n" + item_list

    # Set up the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:", e)



 
from yad2_scraper import fetch_vehicle_category, OrderVehiclesBy
i=1
count =1
good_prices = []
links = []

while (True):
    try:
        category = fetch_vehicle_category(
            "cars",
            page=i,
            price_range=(10000, 45000),
            year_range=(2010, 2023),
            order_by=OrderVehiclesBy.DATE 
        )
        category.load_next_data()
    except:
        break
    cars = category.get_tags()
    for car in cars:
        name = getattr(car, 'model', 'No name')
        year = getattr(car, 'year', 'No year')
        price = getattr(car, 'price_string', 'No price')
        hand = getattr(car, 'hand', 'No hand')
        link = getattr(car, 'relative_link', None)
        marketing = getattr(car, 'marketing_text', None)
        f_marketing =  " ".join(str(marketing).split(' ')[0:1])
        print(name + str(year))
        print(i)
        carzone_price = carzone(name,year,f_marketing) 
        if carzone_price != None:
            num = percentage_change(int(clean_price(carzone_price)), int(clean_price(price)))

            if num > 34 and num <75:
                if(link != None and price != None):
                    print("https://www.yad2.co.il/vehicles/"+link)
                    print(f"og price is {price} and mehiron price {carzone_price}")
                    to_save = "https://www.yad2.co.il/vehicles/"+link+f" \n og price is {price} and mehiron price {carzone_price}"
                    links.append("https://www.yad2.co.il/vehicles/"+link)
                    good_prices.append(to_save)
                    print(good_prices)
                    
                    # send_str_email(
                    #     sender_email="beridayan2008@gmail.com",
                    #     receiver_email="icon333@gmail.com",
                    #     app_password="qapuzlpqfeiueerl",  # No spaces!
                    #     subject=f"Filtered Cars from Yad2 {count}",
                    #     item_list=to_save)

                    send_str_email(
                         sender_email="beridayan2008@gmail.com",
                           receiver_email="beridayan2008@gmail.com",
                         app_password="qapuzlpqfeiueerl",  # No spaces!
                         subject=f"Filtered Cars from Yad2 {count}",
                         item_list=to_save)
                    count+=1

            else:
                print('change is less then 30 ' + str(num))
                print(f"og price is {price} and mehiron price {carzone_price}")
    i+=1
   
    if i ==6:
        send_list_email(
            sender_email="beridayan2008@gmail.com",
            receiver_email="beridayan2008@gmail.com",
            app_password="qapuzlpqfeiueerl",  # No spaces!
            subject=f"full list filterd cars ",
            item_list=good_prices)
        break