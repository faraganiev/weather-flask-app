import requests
from datetime import datetime

def get_weather_for_city(city):
    # Геокодирование
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
    geo_response = requests.get(geocode_url)
    if geo_response.status_code != 200:
        return {"error": "Ошибка геокодирования"}

    geo_data = geo_response.json()
    results = geo_data.get("results")
    if not results:
        return {"error": "Город не найден"}

    location = results[0]
    latitude = location["latitude"]
    longitude = location["longitude"]
    country = location.get("country", "Неизвестно")

    # Погода
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
        f"&current_weather=true&timezone=auto"
    )
    weather_response = requests.get(weather_url)
    if weather_response.status_code != 200:
        return {"error": "Ошибка получения прогноза"}

    weather_data = weather_response.json().get("current_weather", {})
    if not weather_data:
        return {"error": "Нет данных о погоде"}

    # Время в человеко-читаемом виде
    iso_time = weather_data.get("time")
    formatted_time = datetime.fromisoformat(iso_time).strftime("%d.%m.%Y, %H:%M") if iso_time else "Нет времени"

    # Расшифровка кода погоды
    WEATHER_CODES = {
        0: "Ясно ☀",
        1: "Преимущественно ясно 🌤",
        2: "Малооблачно ⛅",
        3: "Облачно ☁",
        45: "Туман 🌫",
        48: "Инейный туман ❄",
        51: "Лёгкая морось 🌧",
        61: "Слабый дождь 🌦",
        80: "Ливень 🌧",
        95: "Гроза ⛈",
    }
    description = WEATHER_CODES.get(weather_data.get("weathercode"), "Неизвестно")

    return {
        "temperature": weather_data.get("temperature"),
        "windspeed": weather_data.get("windspeed"),
        "time": formatted_time,
        "city": city.title(),
        "country": country,
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
    }
