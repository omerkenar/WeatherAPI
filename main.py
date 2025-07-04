import sys
import os
from time import process_time

import requests

from PyQt5.QtGui import QPixmap, QPainter, QIcon, QPalette, QColor
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt,QTimer

class WeatherApp(QWidget):

    def __init__(self):
        super().__init__()
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Bilgileri Getir", self)
        self.location_button = QPushButton("Konumdan Getir", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.background = QPixmap(self.resource_path(("background.jpg")))
        self.dummy_label = QLabel(self)
        self.initUI()

    @staticmethod
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

    def initUI(self):
        self.setWindowTitle("Weather App")
        self.setWindowIcon(QIcon(self.resource_path("icon.png")))

        vbox = QVBoxLayout()
        vbox.addWidget(self.dummy_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.location_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)


        self.setLayout(vbox)

        self.dummy_label.setFocus()

        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)


        self.city_input.setPlaceholderText("Şehir Adı")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.location_button.setObjectName("location_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")


        palette = self.city_input.palette()
        palette.setColor(QPalette.PlaceholderText, QColor("#ffffff"))
        self.city_input.setPalette(palette)

        self.setFixedSize(450, 500)



        self.setStyleSheet("""           
                            
            QLabel, QPushButton{
                background: transparent;
                font-family: calibri;
            }
            
            QLineEdit#city_input{
                font-size: 40px;
                color: white;
                background: transparent;
                border: none;
                border-bottom: 2px solid white;
                border-top: 2px solid white;
            }
            
            QLineEdit#city_input::placeholder{
                color: darkgray;
            }
            
            QPushButton#get_weather_button{
                font-size: 30px;
                font-weight: bold;
                background-color: #5F9EA0;
            }          
             
            QPushButton#location_button{
                font-size: 30px;
                font-weight: bold;
                background-color: #5F9EA0;
            }
            
            QLabel#temperature_label{
                font-size: 75px;
                color: white;
            }
            
            QLabel#emoji_label{
                font-size: 100px;
                font-family: Segoe UI emoji;
                color: white;
            }
            
            QLabel#description_label{
                font-size: 50px;
                color: white;
            }                   
                 
        """)



        self.get_weather_button.clicked.connect(self.get_weather)
        self.location_button.clicked.connect(self.get_location_and_weather)


    def get_location_and_weather(self):
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()

            if data["status"] == "success":
                city = data["city"]
                self.city_input.setText(city)
                self.get_weather_by_city(city)
            else:
                self.display_error("Konum alınamadı.")
        except Exception as e:
            self.display_error(f"Konum hatası:\n{e}")

    def get_weather(self):

        api_key = "5e51448dac9304ffc5ed10e19d0fd4c9"
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=tr"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)
        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not found:\nCity not found")
                case 500:
                    self.display_error("Internal Server Error:\nPlease try again later")
                case 502:
                    self.display_error("Bad Getaway:\nInvalid response from the server")
                case 503:
                    self.display_error("Service Unavailable:\nServer is down")
                case 504:
                    self.display_error("Getaway Timeout:\nNo response from the server")
                case _:
                    self.display_error(f"HTTP error occurred:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")

        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")

        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck your URL")

        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_kelvin = data["main"]["temp"]
        temperature_celsius = temperature_kelvin - 273.15
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]

        self.temperature_label.setText(f"{temperature_celsius:.0f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(weather_description.upper())

    def get_weather_by_city(self, city):
        api_key = "5e51448dac9304ffc5ed10e19d0fd4c9"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=tr"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:

               self.display_weather(data)
            else:
               self.display_error("Şehir bulunamadı.")
        except Exception as e:
               self.display_error(f"Hata oluştu:\n{e}")

    @staticmethod
    def get_weather_emoji(weather_id):

        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "❄️"
        elif 701 <= weather_id <= 741:
            return "🌫️"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""




if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
