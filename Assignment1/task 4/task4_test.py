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
firebase_url = 'https://testkivy-b43b1-default-rtdb.europe-west1.firebasedatabase.app/.json'
# https://kivymd.readthedocs.io/en/latest/themes/ 
# https://kivymd.readthedocs.io/en/latest/components/ 
KV = '''
ScreenManager:
    WeatherScreen:

<WeatherScreen>:
    name: "weather"
    md_bg_color: [0.1, 0.1, 0.12, 1] 

    FloatLayout:

        MDCard:
            orientation: "vertical"
            padding: "16dp"
            spacing: "10dp"
            size_hint: 0.9, 0.35
            pos_hint: {"center_x": 0.5, "top": 0.60}
            elevation: 2
            md_bg_color: [0.15, 0.15, 0.18, 1]
            radius: [12, 12, 12, 12]
            
            MDBoxLayout:
                orientation: "horizontal"
                adaptive_height: True
                MDIcon:
                    icon: "thermometer"
                    theme_text_color: "Custom"
                    text_color: [0.0, 0.6, 0.55, 1]
                MDLabel:
                    text: f"Temperature: {root.label_temp}"
                    theme_text_color: "Custom"
                    text_color: [0.9, 0.9, 0.9, 1]

            MDBoxLayout:
                orientation: "horizontal"
                adaptive_height: True
                MDIcon:
                    icon: "water-percent"
                    theme_text_color: "Custom"
                    text_color: [0.0, 0.6, 0.55, 1]
                MDLabel:
                    text: f"Humidity: {root.label_humidity}"
                    theme_text_color: "Custom"
                    text_color: [0.9, 0.9, 0.9, 1]

            MDBoxLayout:
                orientation: "horizontal"
                adaptive_height: True
                MDIcon:
                    icon: "gauge"
                    theme_text_color: "Custom"
                    text_color: [0.0, 0.6, 0.55, 1]
                MDLabel:
                    text: f"Pressure: {root.label_pressure}"
                    theme_text_color: "Custom"
                    text_color: [0.9, 0.9, 0.9, 1]

            MDBoxLayout:
                orientation: "horizontal"
                adaptive_height: True
                MDIcon:
                    icon: "eye-outline"
                    theme_text_color: "Custom"
                    text_color: [0.0, 0.6, 0.55, 1]
                MDLabel:
                    text: f"Visibility: {root.label_visibility}"
                    theme_text_color: "Custom"
                    text_color: [0.9, 0.9, 0.9, 1]

            MDSeparator:
                color: [0.3, 0.3, 0.35, 1]
            
            MDLabel:
                text: f"Status: {root.status_msg}"
                theme_text_color: "Hint"
                font_style: "Caption"
                halign: "center"
                text_color: [0.6, 0.6, 0.6, 1]

        # 
        MDRaisedButton:
            text: "Collect and save weather data"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5, "top": 0.70}
            md_bg_color: [0.0, 0.6, 0.55, 1]
            text_color: [1, 1, 1, 1]
            elevation: 2
            on_release: root.get_weather()

        # 
        MDTextField:
            id: city_input
            hint_text: "Write a city (ex. stockholm)"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5, "top": 0.82}
            
            mode: "rectangle"
            line_color_normal: [1, 1, 1, 1]
            hint_text_color_normal: [0.7, 0.7, 0.7, 1]
            line_color_focus: [0.0, 0.6, 0.55, 1]
            text_color_normal: [1, 1, 1, 1]
            text_color_focus: [1, 1, 1, 1]

        # 
        MDLabel:
            text: "Group 7 Weather Scraper"
            halign: "center"
            
            pos_hint: {"top": 0.95, "center_x": 0.5}
            
            size_hint_y: None
            height: "50dp"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: [0.0, 0.6, 0.55, 1] 
            bold: True
'''

class WeatherScreen(Screen):
    # UI Properties linked to the labels in the kivy app for automatic updates
    label_temp = StringProperty()
    label_humidity = StringProperty()
    label_pressure = StringProperty()
    label_visibility = StringProperty()
    status_msg = StringProperty("Waiting for data...")

    def get_weather(self):
        # Retrieve and normalize the city name from the UI input field
        city = self.ids.city_input.text.lower()
        # Attempt to fetch data from web sources (TimeAndDate or Wunderground)
        weather_data = self.scrape_weather(city)
        # Check if data was successfully retrieved to avoid crashing the app
        if weather_data:
            # Update the UI properties with the newly scraped data
            self.label_temp = weather_data["temperature"]
            self.label_humidity = weather_data["humidity"]
            self.label_pressure = weather_data["pressure"]
            self.label_visibility = weather_data["visibility"]
            #Replicate data to three different storage locations
            self.save_to_txt(weather_data)
            self.save_to_sqlite(weather_data)
            self.save_to_firebase(weather_data)
            # Provide feedback to the user via the UI status message
            self.status_msg = "Weather data saved"

    def scrape_weather(self, city):
        # Define target URLs for both weather sources using the provided city name
        url1 = f"https://www.timeanddate.com/weather/sweden/{city}"
        url2 = f"https://www.wunderground.com/weather/se/{city}"

        try:
            # Send HTTP request to the first source
            r1 = requests.get(url1, headers=headers)
            soup1 = BeautifulSoup(r1.content, "html.parser")
            # Extract specific weather attributes using HTML tags and IDs
            temperature = soup1.find("div", {"id": "qlook"}).find_next("div", {"class": "h2"}).text
            humidity = soup1.find("th", string="Humidity: ").find_next("td").text
            pressure = soup1.find("th", string="Pressure: ").find_next("td").text
            visibility = soup1.find("th", string="Visibility: ").find_next("td").text
            # Specific check to handle missing visibility values (N/A)
            if "N/A" in visibility:
                visibility = soup1.find("th", string="Visibility").find_next("td").text
                # Return successfully scraped data as a dictionary for storage
            return {
                "city": city, "temperature": temperature, "humidity": humidity,
                "pressure": pressure, "visibility": visibility
             }
        except Exception as e:
            # Log failure for the first source and proceed to the fallback source
            print(f"Failure, could not find the data on time and data. {e}")
            try:
                r2 = requests.get(url2, headers=headers)
                soup2 = BeautifulSoup(r2.content, "html.parser")
                temperature = soup2.find("span", {"class": "wu-unit-temperature"}).find("span", {
                    "class": "wu-value wu-value-to"}).text
                # Convert temperature from Fahrenheit to Celsius for consistency
                temperature = (int(temperature)- 32) / 1.8
                temperature = str(temperature)
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
                # Final error handling if both sources are unavailable or city is not found
                print(f"Failure, could not find the data on wunderground please enter a new city. {e}")

    def save_to_txt(self, data):
        # Open the file in 'append' mode ("a") to add new data without deleting old logs
        # Using utf-8 encoding to handle special characters
        with open("weather_1.txt", "a", encoding="utf-8") as f:
            for value in data.values():
                # Iterate through the dictionary values to store each data point
                f.write(f"{value}\n")

    def save_to_sqlite(self, data):
        try:
            # Connect to the local database file (creates it if it doesn't exist)
            con = sqlite3.connect("weather.db")
            cur = con.cursor()
            # Ensure the table exists before attempting an insert
            # 'id' is set to AUTOINCREMENT to handle primary keys automatically
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
            # Insert data using named placeholders to map the dictionary keys directly
            # We explicitly name the 5 columns to allow the 'id' column to auto-populate
            cur.execute("""INSERT INTO weather_data (city, temperature, humidity, pressure, visibility)
                           VALUES (:city, :temperature, :humidity, :pressure, :visibility)""", data)
            con.commit()
            # Save changes to the database
            print("Data saved successfully")
            con.close()
            # Always close the connection to prevent database locks
        except Exception as e:
            #Log errors to console to prevent the application from crashing
            print(f"SQLite error: {e}")

    def save_to_firebase(self, data):
        try:
            # Send an HTTP POST request with the weather dictionary as a JSON payload
            # This allows for cloud-based data backup and synchronization
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