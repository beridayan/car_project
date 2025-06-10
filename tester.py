import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import re

def check_yad2_conditions_with_hand_km_and_date(url):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)

    driver.get(url)
    wait = WebDriverWait(driver, 20)

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "details-item_itemValue__r0R14")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-testid="term"]')))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "report-ad_createdAt__MhAb0")))
    except Exception as e:
        print(f"Waiting for elements failed: {e}")
        driver.quit()
        return False

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find first hand between 0 and 6 inclusive
    hand = None
    for span in soup.find_all("span", class_="details-item_itemValue__r0R14"):
        try:
            val = int(span.text.strip())
            if 0 <= val <= 6:
                hand = val
                break
        except Exception as e:
            print(f"Error parsing hand value: {e}")
            continue
    print(f"Extracted hand: {hand}")

    # Find any km > 60000 (take the first that meets this)
    km = None
    for km_span in soup.find_all("span", {"data-testid": "term"}):
        try:
            km_val = int(km_span.text.strip().replace(",", ""))
            if km_val > 60000:
                km = km_val
                break
        except Exception as e:
            print(f"Error parsing km value: {e}")
            continue
    print(f"Extracted km: {km}")

    date_span = soup.find("span", class_="report-ad_createdAt__MhAb0")
    if date_span:
        text = date_span.get_text(strip=True)
        # Extract date string with regex to find dd/mm/yy pattern
        match = re.search(r"\d{2}/\d{2}/\d{2}", text)
        if match:
            date_str = match.group(0)
            try:
                post_date = datetime.strptime(date_str, "%d/%m/%y").date()
                today = datetime.today().date()
                three_days_ago = today - timedelta(days=3)
                date_ok = post_date >= three_days_ago
                print(f"Post date: {post_date}, Today: {today}, Date OK? {date_ok}")
            except Exception as e:
                print(f"Error parsing date: {e}")
                date_ok = False
        else:
            print("Date pattern not found in text")
            date_ok = False
    else:
        print("Date span not found")
        date_ok = False
        driver.quit()

    if hand<=2 and km <=140000 and date_ok:
        print("All conditions met, returning True")
        return True

    print("Conditions not met, returning False")
    return False


# Example usage
url = "https://www.yad2.co.il/vehicles/item/3cx73jfe?opened-from=feed&component-type=main_feed&spot=standard&location=7&pagination=1"
print(check_yad2_conditions_with_hand_km_and_date(url))
