
import pickle
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def main():
    profile_path = "C:\\Users\\alaad\\AppData\\Local\\Google\\Chrome\\User Data"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Exclude the collection of enable-automation switches
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-extensions")

    # Turn-off userAutomationExtension
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument('profile-directory=Default')
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    # driver.get("file:///C:/Users/alaad/Downloads/uber/1vsdispatch.uber.com.html")
    driver.get("https://vsdispatch.uber.com/")

    time.sleep(1)  # Polling-Intervall

    cookies = driver.get_cookies()

    pickle.dump(cookies, open("cookies12.pkl", "wb"))

main()