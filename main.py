import threading
import requests
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget

API_KEY = '1bfacbe692f213fd1a48cf10f6edae3d'
url = 'http://api.openweathermap.org/data/2.5/weather'


class WeatherThread(threading.Thread):
    def __init__(self, city):
        super().__init__()
        self.city = city
        self.result = None

    def run(self):
        response = requests.get(f'{url}?q={self.city}&appid={API_KEY}')
        data = response.json()
        self.result = (data["weather"][0]["description"], data["main"]["temp"])


def save_to_database(city, description, temperature):
    conn = sqlite3.connect('havadurumu.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS il_info(
    id INTEGER PRIMARY KEY,
    il_ismi TEXT,
    durum TEXT,
    sicaklik REAL)''')
    cursor.execute('INSERT INTO il_info (il_ismi, durum, sicaklik) VALUES (?, ?, ?)', (city, description, temperature))
    conn.commit()
    conn.close()


class HavaDurumuApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Hava Durumu Uygulaması')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.city_input = QLineEdit()
        layout.addWidget(self.city_input)

        self.get_weather_button = QPushButton('Hava Durumu Al')
        self.get_weather_button.clicked.connect(self.get_weather)
        layout.addWidget(self.get_weather_button)

        self.weather_label = QLabel('Hava Durumu: ')
        layout.addWidget(self.weather_label)

        self.temperature_label = QLabel('Sıcaklık: ')
        layout.addWidget(self.temperature_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def get_weather(self):
        city = self.city_input.text()

        weather_thread = WeatherThread(city)
        weather_thread.start()
        weather_thread.join()

        description, temperature = weather_thread.result
        self.weather_label.setText(f'Hava Durumu: {description}')
        self.temperature_label.setText(f'Sıcaklık: {temperature-273}°C')

        save_thread = threading.Thread(target=save_to_database, args=(city, description, temperature))
        save_thread.start()
        save_thread.join()


if __name__ == "__main__":
    app = QApplication([])
    window = HavaDurumuApp()
    window.show()
    app.exec_()
