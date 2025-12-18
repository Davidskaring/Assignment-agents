from bs4 import BeautifulSoup
import requests
import sys
import sqlite3
import pandas as pd

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
headers = {"user-agent": USER_AGENT}

# city_input = input("What city") // ska skrivas som en input 
city = input() # Här ska city input läggas in
country = "sweden"   # Behövs för TimeAndDate
country_code = "se"  # Behövs ofta för Wunderground (iso-kod)

url1 = f"https://www.timeanddate.com/weather/sweden/{city}"
url2 = f"https://www.wunderground.com/weather/se/{city}"

r1 = requests.get(url1, headers=headers)
r2 = requests.get(url2, headers=headers)

soup1 = BeautifulSoup(r1.content, "html.parser")
soup2 = BeautifulSoup(r2.content, "html.parser")

print("Status TimeAndDate:", r1.status_code)
print("Status Wunderground:", r2.status_code)

#Try catch sats for collecting weather information.
try:
    temperature = soup1.find("div", {"id": "qlook"}).find_next("div", {"class": "h2"}).text
    humidity =  soup1.find("th", string="Humidity: ").find_next("td").text
    pressure = soup1.find("th", string="Pressure: ").find_next("td").text
    visibility = soup1.find("th", string="Visibility: ").find_next("td").text
    if "N/A" in visibility:
        visibility = soup1.find("th", string="Visibility").find_next("td").text
except:
    print("Failure, could not find the data on time and data")
    try:
        temperature = soup2.find("span",{"class": "wu-unit-temperature"}).find("span",{"class": "wu-value wu-value-to"}).text
        humidity = soup2.find("span",{"class": "wu-unit-humidity"}).find("span",{"class": "wu-value wu-value-to"}).text
        pressure = soup2.find("span",{"class": "wu-unit-pressure"}).find("span",{"class": "wu-value wu-value-to"}).text
        visibility = soup2.find("span",{"class": "wu-unit-distance"}).find("span",{"class": "wu-value wu-value-to"}).text
    except:
        print("Failure, could not find the data on wunderground please enter a new city")

weather = {
    "temperature": temperature,
    "humidity": humidity,
    "pressure": pressure,
    "visibility": visibility,
    "city": city
}

print (city)
print (humidity)
print (temperature)
print (pressure)
print (visibility)

print (weather)

with open("weather_1.txt", "w", encoding="utf-8") as f:
    for value in weather.values():
        f.write(f"{value}\n")

with open("weather_1.txt", "r", encoding="utf-8") as f:
    weather_txt = f.read()
    print(weather_txt)

con = sqlite3.connect("weather.db")
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    temperature TEXT,
    humidity TEXT,
    pressure TEXT,
    visibility TEXT
)
""")
con.commit()
con.close()

def save_to_sqlite(weather):
    try:
        con = sqlite3.connect('weather.db')
        cursor = con.cursor()
        cursor.execute("""
        INSERT INTO weather_data (city, temperature, humidity, pressure, visibility) 
        VALUES (:city, :temperature, :humidity, :pressure, :visibility) """, weather)


        con.commit()
        print("Data saved in weather.db!")

    except Exception as e:
        print(f"Failure: {e}")
    finally:
        con.close()


save_to_sqlite(weather)