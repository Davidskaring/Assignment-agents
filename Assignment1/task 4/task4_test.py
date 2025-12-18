from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.core.window import Window
import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import os

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
headers = {"user-agent": USER_AGENT}
firebase_url = 'https://console.firebase.google.com/u/0/project/testkivy-b43b1/database/testkivy-b43b1-default-rtdb/data/~2F/.json'

KV = '''
ScreenManager:
    WeatherScreen:

<WeatherScreen>:
    name: "weather"
    FloatLayout:
        MDLabel:
            text: "Weather Scraper Pro"
            halign: "center"
            pos_hint: {"top": 0.95}
            font_style: "H4"

        MDTextField:
            id: city_input
            hint_text: "Ange stad (t.ex. falun)"
            pos_hint: {"center_x": 0.5, "top": 0.8}
            size_hint_x: 0.8

        MDRaisedButton:
            text: "Hämta och Spara Väder"
            pos_hint: {"center_x": 0.5, "top": 0.7}
            size_hint_x: 0.8
            on_release: root.get_weather()

        MDCard:
            orientation: "vertical"
            padding: "10dp"
            size_hint: 0.9, 0.35
            pos_hint: {"center_x": 0.5, "top": 0.6}
            elevation: 2

            MDLabel:
                text: f"Temperatur: {root.label_temp}"
                theme_text_color: "Secondary"}"
                theme_text_color: "Secondary"
            MDLabel:
                text: f"Luftfuktighet: {root.label_humidity}"
                theme_text_color: "Secondary"}"
                theme_text_color: "Secondary"
            MDLabel:
                text: f"Tryck: {root.label_pressure}"
                theme_text_color: "Secondary"
            MDLabel:
                text: f"Sikt: {root.label_visibility}"
                theme_text_color: "Secondary"
            MDLabel:
                text: f"Status: {root.status_msg}"
                theme_text_color: "Hint"
                font_style: "Caption"
'''

class WeatherScreen(Screen):
    label_temp = StringProperty()
    label_humidity = StringProperty()
    label_pressure = StringProperty()
    label_visibility = StringProperty()
    status_msg = StringProperty("Waiting for data...")

    def get_weather(self):
        city = self.ids.city_input.text.lower()
        weather_data = self.scrape_weather(city)
        if weather_data:
            self.label_temp = weather_data["temperature"]
            self.label_humidity = weather_data["humidity"]
            self.label_pressure = weather_data["pressure"]
            self.label_visibility = weather_data["visibility"]

            self.save_to_txt(weather_data)
            self.save_to_sqlite(weather_data)
            self.save_to_firebase(weather_data)

            self.status_msg = "Weather data saved"

    def scrape_weather(self, city):
        url1 = f"https://www.timeanddate.com/weather/sweden/{city}"
        url2 = f"https://www.wunderground.com/weather/se/{city}"

        r1 = requests.get(url1, headers=headers)
        r2 = requests.get(url2, headers=headers)

        soup1 = BeautifulSoup(r1.content, "html.parser")
        soup2 = BeautifulSoup(r2.content, "html.parser")

        try:
            temperature = soup1.find("div", {"id": "qlook"}).find_next("div", {"class": "h2"}).text
            humidity = soup1.find("th", string="Humidity: ").find_next("td").text
            pressure = soup1.find("th", string="Pressure: ").find_next("td").text
            visibility = soup1.find("th", string="Visibility: ").find_next("td").text
            if "N/A" in visibility:
                visibility = soup1.find("th", string="Visibility").find_next("td").text
                return {
                    "city": city, "temperature": temperature, "humidity": humidity,
                    "pressure": pressure, "visibility": visibility
                }
        except Exception as e:
            print(f"Failure, could not find the data on time and data. {e}")
            try:
                temperature = soup2.find("span", {"class": "wu-unit-temperature"}).find("span", {
                    "class": "wu-value wu-value-to"}).text
                humidity = soup2.find("span", {"class": "wu-unit-humidity"}).find("span", {
                    "class": "wu-value wu-value-to"}).text
                pressure = soup2.find("span", {"class": "wu-unit-pressure"}).find("span", {
                    "class": "wu-value wu-value-to"}).text
                visibility = soup2.find("span", {"class": "wu-unit-distance"}).find("span", {
                    "class": "wu-value wu-value-to"}).text
                return {
                    "city": city, "temperature": temperature, "humidity": humidity,
                    "pressure": pressure, "visibility": visibility
                }
            except Exception as e:
                print(f"Failure, could not find the data on wunderground please enter a new city. {e}")

    def save_to_txt(self, data):
        with open("weather_1.txt", "a", encoding="utf-8") as f:
            for value in data.values():
                f.write(f"{value}\n")

    def save_to_sqlite(self, data):
        try:
            con = sqlite3.connect("weather.db")
            cur = con.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS weather_data
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               city
                               TEXT,
                               temperature
                               TEXT,
                               humidity
                               TEXT,
                               pressure
                               TEXT,
                               visibility
                               TEXT
                           )""")
            cur.execute("""INSERT INTO weather_data (city, temperature, humidity, pressure, visibility)
                           VALUES (:city, :temperature, :humidity, :pressure, :visibility)""", data)
            con.commit()
            print("Data saved successfully")
            con.close()
        except Exception as e:
            print(f"SQLite error: {e}")

    def save_to_firebase(self, data):
        try:
            requests.post(url=firebase_url, json=data)
        except Exception as e:
            print(f"Firebase error: {e}")

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        Window.size = (400, 600)
        return Builder.load_string(KV)

if __name__ == "__main__":
    MainApp().run()