import asyncio
import pickle
import time

from selenium import webdriver
from aiohttp import ClientSession
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service



def main():

    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Exclude the collection of enable-automation switches
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-extensions")

    # Turn-off userAutomationExtension
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")

    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    # driver.get("file:///C:/Users/alaad/Downloads/uber/1vsdispatch.uber.com.html")
    driver.get("https://vsdispatch.uber.com/")

    cookies = pickle.load(open("cookies12.pkl", "rb"))

    for cookie in cookies:
        cookie['domain'] = ".uber.com"

        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(e)

    driver.get("https://vsdispatch.uber.com/")
    time.sleep(1)
    print(len(driver.find_elements(By.CSS_SELECTOR, 'tr.MuiTableRow-root')))
    time.sleep(120)

main()