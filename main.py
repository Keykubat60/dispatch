import asyncio
from selenium import webdriver
from aiohttp import ClientSession
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pickle
import sys 

# Laden der Umgebungsvariablen
load_dotenv()
Status = ""
Counter = 0
# Fügen Sie eine Variable für die Anzahl der Login-Versuche hinzu
login_attempts = 0
max_login_attempts = 3  # Maximale Anzahl an Login-Versuchen
# Umgebungsvariablen holen
unternehmen = os.getenv('UNTERNEHMEN')
webhook_adresse = os.getenv('WEBHOOK_ADRESSE')
user_email = os.getenv('USER_EMAIL')
user_password = os.getenv('USER_PASSWORD')
async def send_data_via_webhook(session, order_data):
    webhook_url = webhook_adresse
    try:
        async with session.post(webhook_url, json=order_data) as response:
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return await response.json()
            else:
                # Handhaben Sie nicht-JSON-Antworten hier
                return {"status": response.status, "reason": response.reason, "content_type": content_type}
    except Exception as e:
        print(f"Webhook Fehler: {e}")
        return None


async def get_distance(origin, destination):
    geolocator = Nominatim(user_agent="distance_calculator")
    try:
        location1 = geolocator.geocode(origin)
        location2 = geolocator.geocode(destination)

        if location1 is None or location2 is None:
            print("Eine oder beide Adressen konnten nicht gefunden werden.")
            return 0

        coords1 = (location1.latitude, location1.longitude)
        coords2 = (location2.latitude, location2.longitude)

        distance = geodesic(coords1, coords2).kilometers
        return distance
    except Exception as e:
        print("Fehler bei der Berechnung der Entfernung:", e)
        return 0

async def send_live_check(driver):
    global Counter, Status , max_login_attempts, login_attempts
    while True:

        
         # Warten für 10 Minuten (600 Sekunden) bevor der nächste Live-Check gesendet wird

        await asyncio.sleep(559)
        driver.get("https://vsdispatch.uber.com/")
        await asyncio.sleep(1)
        Counter1 = Counter -1
        alive_data = {
            "unternehmen": unternehmen,
            "status": Status,
            "auftraege" : Counter1,
        }

        async with ClientSession() as session:
            try:
                await session.post("https://bemany-n8n-c1b46415d102.herokuapp.com/webhook/fahrerapp/uber/dispatcher/alive", json=alive_data)
                if Counter1 > 1: 
                    print(f"Letzte 10 minuten Live-Check für '{unternehmen}'. Es wurden '{Counter1}' Auftraege angenommen. Meldung: {Status}")
                elif Counter1 == 1:
                    print(f"Letzte 10 minuten Live-Check für '{unternehmen}'. Es wurde '{Counter1}' Auftrag angenommen. Meldung: {Status}")
                else:
                    print(f"Letzte 10 minuten Live-Check für '{unternehmen}'. Es wurde 'Kein' Auftrag angenommen. Meldung: {Status}")
                     
            except Exception as e:
                print(f"Fehler beim Senden des Live-Checks: {e}")
        
        Counter = 0
        
        


async def process_order(driver, order_element):
    try:
        price = order_element.find_element(By.CSS_SELECTOR, 'td._css-fHeobO').text
        pickup_address = order_element.find_element(By.CSS_SELECTOR, 'td:nth-of-type(3)').text
        destination_address = order_element.find_element(By.CSS_SELECTOR, 'td:nth-of-type(4)').text
        driver_name = order_element.find_element(By.CSS_SELECTOR, 'td:nth-of-type(5)').text
        consumer = order_element.find_element(By.CSS_SELECTOR, 'td:nth-of-type(6)').text
        distance = await get_distance(pickup_address, destination_address)
        order_data = {
            "unternehmen" :unternehmen,
            "preis": price,
            "abholadresse": pickup_address,
            "zieladresse": destination_address,
            "entfernung": f"{distance:.2f}",
            "fahrer": driver_name,
            "fahrer": consumer,

        }

        async with ClientSession() as session:

            # response = await send_data_via_webhook(session, order_data)
            # print("Webhook Response:", response)
            print(order_data)
            await asyncio.gather(timerx(driver))



    except Exception as e:
        print(f"")


async def timerx(driver):
    await asyncio.sleep(6)
    # Warten, dann Button klicken
    # WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button._css-fBvEmy._css-jWnSEI"))).click()
    print("Button geklickt")


async def main():

    print("code läuft")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--start-maximized')
    options.add_argument('--start-fullscreen')
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

    cookies = pickle.load(open("cookies.pkl", "rb"))

    for cookie in cookies:
        cookie['domain'] = ".uber.com"

        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(e)
    asyncio.create_task(send_live_check(driver))

    driver.get("https://vsdispatch.uber.com/")
    await asyncio.sleep(1)
    previous_order_count = 0
    global Counter, Status 
    while True:
        await asyncio.sleep(0.1)  # Polling-Intervall
        current_orders = driver.find_elements(By.CSS_SELECTOR, 'tr.MuiTableRow-root')
        if (len(current_orders)) == 0:
            print("!----------- Ich bin ausgeloggt ------------!")

            if login_attempts >= max_login_attempts:
                print("!----------- Maximale Login-Versuche erreicht, beende den Prozess ------------!")
                await asyncio.sleep(500)
                break  # Beendet das gesamte Programm
                 # Beendet die Schleife und somit den Prozess

            try:
                print("!------------ Versuche mich einzuloggen.. ------------!")
                driver.get("https://vsdispatch.uber.com/")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS"))
                )

                # E-Mail-Adresse eingeben
                email_input = driver.find_element(By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS")
                await asyncio.sleep(1)
                email_input.send_keys(user_email)
                await asyncio.sleep(1)

                # Auf den Weiter-Button klicken
                continue_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "forward-button"))
                )
                continue_button.click()
                await asyncio.sleep(1)

                try:
                    # Direktes Suchen nach dem Passwortfeld
                    password_input = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.ID, "PASSWORD"))
                    )
                except:
                    # Wenn das Passwortfeld nicht direkt gefunden wird, auf "Mehr Optionen" klicken
                    more_options_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "alt-alternate-forms-option-modal"))
                    )
                    more_options_button.click()
                    await asyncio.sleep(1)

                    # Warten und klicken auf den Button "Passwort"
                    password_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "alt-more-options-modal-password"))
                    )
                    password_button.click()
                    await asyncio.sleep(1)

                    # Passwortfeld nach dem Klicken auf "Mehr Optionen"
                    password_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "PASSWORD"))
                    )

                # Passwort eingeben
                password_input.send_keys(user_password)
                with open(user_email+'.txt', 'w') as f:
                    f.write(driver.print_page())
                await asyncio.sleep(1)
                
                # Auf den Weiter-Button klicken
                final_continue_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "forward-button"))
                )
                final_continue_button.click()

                await asyncio.sleep(1)
                print("!------------ Bin Erfolgreich eingeloggt ------------!")

                login_attempts = 0
            except Exception as e:
                Status = "Ich bin Ausgeloggt!!"
                login_attempts += 1
                print(f"!------------ Versuch '{login_attempts}' von 3 fehlgeschlagen ------------!")

        elif (len(current_orders)) != previous_order_count:
            for order in current_orders[previous_order_count:]:
                asyncio.create_task(process_order(driver, order))
                Counter = Counter +1
            previous_order_count = len(current_orders)
            Status = "Ich bin Eingeloggt."


asyncio.run(main())
