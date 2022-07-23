import requests
from datetime import datetime
import math
import smtplib
import time
import os
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
MY_LAT = os.getenv('MY_LAT')
MY_LONG = os.getenv('MY_LONG')

# Sunset and Sunrise only needs to run once
parameters = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0,
}


def is_iss_overhead():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    # Your position is within +5 or -5 degrees of the ISS position.
    lat_closeness = math.isclose(MY_LAT, iss_latitude, abs_tol=5)
    lng_closeness = math.isclose(MY_LONG, iss_longitude, abs_tol=5)

    if lat_closeness and lng_closeness:
        return True


def is_night_time():
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])
    time_now = datetime.now().hour

    if time_now >= sunset or time_now <= sunrise:
        return True


while True:
    time.sleep(60)
    if is_iss_overhead() and is_night_time():
            print("Success")
            with smtplib.SMTP("smtp.gmail.com", 587) as con:
                con.starttls()
                con.login(user=USER, password=PASSWORD)
                con.sendmail(
                    from_addr=USER,
                    to_addrs="nicolajlpedersen@gmail.com",
                    msg=f"Subject:ISS is CLOSE\n\nLOOK UP!"
                )
                print("Email send")



