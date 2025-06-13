from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re


from flask import Flask, render_template, request
import threading
import webbrowser

from yad2_scraper import fetch_vehicle_category, OrderVehiclesBy

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_yad2_conditions_with_hand_km_and_date(url,maxdaysup,maxhand,maxkm):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)

    try:
        # 1) Load page & wait for all three elements
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "details-item_itemValue__r0R14")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-testid="term"]')))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "report-ad_createdAt__MhAb0")))

        # 2) Parse the page
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # — hand (0–6)
        hand = None
        for span in soup.find_all("span", class_="details-item_itemValue__r0R14"):
            try:
                val = int(span.text.strip())
                if 0 <= val <= 6:
                    hand = val
                    break
            except ValueError:
                continue

        print(f"Extracted hand: {hand}")

        # — km > 60000
        km = None
        for km_span in soup.find_all("span", {"data-testid": "term"}):
            try:
                km_val = int(km_span.text.strip().replace(",", ""))
                if km_val > 60000:
                    km = km_val
                    break
            except ValueError:
                continue

        print(f"Extracted km: {km}")

        # — date within last 10 days
        date_span = soup.find("span", class_="report-ad_createdAt__MhAb0")
        date_ok = False
        if date_span:
            text = date_span.get_text(strip=True)
            match = re.search(r"\d{2}/\d{2}/\d{2}", text)
            if match:
                date_str = match.group(0)
                try:
                    post_date = datetime.strptime(date_str, "%d/%m/%y").date()
                    today = datetime.today().date()
                    ten_days_ago = today - timedelta(days=maxdaysup)
                    date_ok = post_date >= ten_days_ago
                    print(f"Post date: {post_date}, Today: {today}, Date OK? {date_ok}")
                except ValueError:
                    print("Error parsing date string")
        else:
            print("Date span not found")

        # 3) Final check (ensure hand and km are not None)
        if hand is not None and km is not None and hand <= maxhand and km <= maxkm and date_ok:
            print("All conditions met, returning True")
            return True

        print("Conditions not met, returning False")
        return False

    finally:
        # ALWAYS runs, even if you return or an exception is thrown
        driver.quit()


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

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



 
def main_app(minprice, maxprice , minyear, maxyear,maxdaysup,maxhand,maxkm,email,pages_to_run):
    i=1
    count =1
    good_prices = []

    while (True):
        try:
            category = fetch_vehicle_category(
                "cars",
                page=i,
                price_range=(minprice, maxprice),
                year_range=(minyear, maxyear),
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

                if num > 32 and num <90:
                    if(link != None and price != None):
                        print("found a big orice change, checking if it is any good")
                        f_link = "https://www.yad2.co.il/vehicles/"+link
                        if(check_yad2_conditions_with_hand_km_and_date(f_link,maxdaysup,maxhand,maxkm)):
                            print(f_link)
                            print(f"og price is {price} and mehiron price {carzone_price}")
                            
                            to_save = f_link+f" \n og price is {price} and mehiron price {carzone_price}"
                            good_prices.append(to_save)
                            print(good_prices)

                            send_str_email(
                                sender_email="beridayan2008@gmail.com",
                                receiver_email=email,
                                app_password="qapuzlpqfeiueerl",  # No spaces!
                                subject=f"Filtered Cars from Yad2 {count}",
                                item_list=to_save)
                            count+=1

                else:
                    print('change is less then 30 ' + str(num))
                    print(f"og price is {price} and mehiron price {carzone_price}")
        i+=1
    
        if i ==pages_to_run:
            send_list_email(
                sender_email="beridayan2008@gmail.com",
                receiver_email=email,
                app_password="qapuzlpqfeiueerl",  # No spaces!
                subject=f"full list filterd cars ",
                item_list=good_prices)
            break



app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        minprice = int(request.form["minprice"])
        maxprice = int(request.form["maxprice"])
        minyear = int(request.form["minyear"])
        maxyear = int(request.form["maxyear"])
        maxdaysup = int(request.form["maxdaysup"])
        maxhand = int(request.form["maxhand"])
        maxkm = int(request.form["maxkm"])
        email = request.form["email"]
        pages_to_run = int(request.form["pages_to_run"])

        # Run main_app in a new thread to avoid blocking the Flask app
        threading.Thread(target=main_app, args=(minprice, maxprice, minyear, maxyear, maxdaysup, maxhand, maxkm, email, pages_to_run)).start()

        return "<h2>✅ Your request is being processed. You'll get an email once the results are ready.</h2>"
    
    return render_template("index.html")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()  # פותח את הדפדפן אחרי דיליי קטן
    app.run(debug=False)
