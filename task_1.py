#task4.1

import requests
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import io
import os
from datetime import datetime

# Константы
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"

# Города по умолчанию
DEFAULT_CITIES = ["Moscow", "Saint Petersburg", "Novosibirsk", "Tomsk"]

# Глобальные переменные
current_icon = None
api_key = ""


# ------------------ Логика ------------------


# Функция получения данных о погод е
def get_weather(city_name):
    global api_key
    try:
        params = {
            "q": city_name,
            "appid": api_key,
            "units": "metric",
            "lang": "ru"
        }
        response = requests.get(BASE_URL, params = params, timeout = 10)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            messagebox.showerror("Ошибка", "Неверный API ключ!")
            return None
        elif response.status_code == 404:
            messagebox.showerror("Ошибка", f"Город '{city_name}' не найден!")
            return None
        else:
            messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения: {e}")
        return None


# Функция загрузки иконки погоды
def load_weather_icon(icon_code):
    global current_icon
    try:
        url = ICON_URL.format(icon = icon_code)
        response = requests.get(url, timeout = 10)
        if response.status_code == 200:
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            current_icon = ImageTk.PhotoImage(img)
            return current_icon
        return None
    except Exception as e:
        print(f"Ошибка загрузки иконки: {e}")
        return None


# Функция получения описания погоды на русском
def get_weather_description_ru(description):
    descriptions = {
        "clear sky": "Ясное небо",
        "few clouds": "Малооблачно",
        "scattered clouds": "Рассеянные облака",
        "broken clouds": "Облачно с прояснениями",
        "overcast clouds": "Пасмурно",
        "light rain": "Небольшой дождь",
        "moderate rain": "Умеренный дождь",
        "heavy intensity rain": "Сильный дождь",
        "very heavy rain": "Очень сильный дождь",
        "extreme rain": "Проливной дождь",
        "freezing rain": "Ледяной дождь",
        "light snow": "Небольшой снег",
        "snow": "Снег",
        "heavy snow": "Сильный снег",
        "mist": "Туман",
        "fog": "Туман",
        "haze": "Мгла",
        "thunderstorm": "Гроза",
        "thunderstorm with light rain": "Гроза с небольшим дождём",
        "thunderstorm with heavy rain": "Гроза с сильным дождём"
    }
    return descriptions.get(description.lower(), description.capitalize())


# Функция получения направления ветра на русском
def get_wind_direction(degrees):
    if degrees is None:
        return "N/A"
    directions = [
        ("С", 0, 22.5), ("СВ", 22.5, 67.5), ("В", 67.5, 112.5),
        ("ЮВ", 112.5, 157.5), ("Ю", 157.5, 202.5), ("ЮЗ", 202.5, 247.5),
        ("З", 247.5, 292.5), ("СЗ", 292.5, 337.5), ("С", 337.5, 360)
    ]
    for direction, start, end in directions:
        if start <= degrees < end:
            return direction
    return "С"


# Функция обновления отображения погоды
def update_display(data):
    global current_icon

    # Основные данные
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    description = data["weather"][0]["description"]
    icon_code = data["weather"][0]["icon"]
    city_name = data["name"]

    # Дополнительные данные
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    visibility = data.get("visibility", 0) / 1000
    wind_speed = data["wind"]["speed"]
    wind_deg = data["wind"].get("deg")
    clouds = data["clouds"]["all"]
    sunrise = data["sys"]["sunrise"]
    sunset = data["sys"]["sunset"]

    # Преобразование времени
    sunrise_time = datetime.fromtimestamp(sunrise).strftime("%H:%M")
    sunset_time = datetime.fromtimestamp(sunset).strftime("%H:%M")

    # Преобразование давления из гПа в мм рт. ст.
    pressure_mm = int(pressure * 0.75006)

    # Получение направления ветра
    wind_dir = get_wind_direction(wind_deg)

    # Получение описания на русском
    desc_ru = get_weather_description_ru(description)

    # Загрузка иконки
    icon_img = load_weather_icon(icon_code)
    if icon_img:
        icon_label.config(image = current_icon)

    # Обновление меток
    winmain.title(f"Погода - {city_name}")
    temp_label.config(text = f"{temp:.1f}°C")
    feels_label.config(text = f"Ощущается: {feels_like:.1f}°C")
    description_label.config(text = f"{desc_ru}")

    pressure_label.config(text = f"{pressure_mm} мм рт. ст.")
    humidity_label.config(text = f"{humidity}%")
    visibility_label.config(text = f"{visibility:.1f} км")
    wind_label.config(text = f"{wind_speed:.1f} м/с")
    wind_dir_label.config(text = wind_dir)
    clouds_label.config(text = f"{clouds}%")
    sunrise_label.config(text = sunrise_time)
    sunset_label.config(text = sunset_time)


# Функция сохранения API ключа
def save_api_key():
    global api_key
    api_key = api_entry.get().strip()
    if not api_key:
        messagebox.showwarning("Внимание", "Введите API ключ!")
        return False
    messagebox.showinfo("Успех", "API ключ сохранён!")
    settings_window.destroy()
    return True


# Функция открытия окна настроек
def open_settings():
    global settings_window, api_entry

    settings_window = tk.Toplevel(winmain)
    settings_window.title("Настройки")
    settings_window.geometry("400x200")
    settings_window.resizable(False, False)
    settings_window.grab_set()

    # Основной фрейм
    settings_frame = ttk.Frame(settings_window, padding = "20")
    settings_frame.pack(fill = "both", expand = True)

    ttk.Label(settings_frame, text = "OpenWeatherMap API", font = ("Segoe UI", 14, "bold")).pack(pady = (0, 15))
    ttk.Label(settings_frame, text = "Введите ваш API ключ:", font = ("Segoe UI", 10)).pack(anchor = "w")

    api_entry = ttk.Entry(settings_frame, font = ("Segoe UI", 10), width = 40)
    api_entry.pack(fill = "x", pady = (5, 15))

    # Вставка существующего ключа если есть
    if api_key:
        api_entry.insert(0, api_key)

    # Кнопки
    btn_frame = ttk.Frame(settings_frame)
    btn_frame.pack(fill = "x", pady = (10, 0))

    ttk.Button(btn_frame, text = "Сохранить", command = save_api_key).pack(side = "left", padx = 5)
    ttk.Button(btn_frame, text = "Отмена", command = settings_window.destroy).pack(side = "left", padx = 5)

    # Ссылка на регистрацию
    link_label = ttk.Label(
        settings_frame,
        text = "Нет ключа? Зарегистрируйтесь на openweathermap.org",
        font = ("Segoe UI", 8),
        foreground = "blue",
        cursor = "hand2"
    )
    link_label.pack(pady = (15, 0))
    link_label.bind("<Button-1>", lambda e: os.startfile("https://openweathermap.org/api"))


# Функция поиска погоды
def search_weather():
    global api_key
    if not api_key:
        messagebox.showwarning("Внимание", "Сначала введите API ключ в настройках!")
        open_settings()
        return

    city = city_entry.get().strip()
    if not city:
        messagebox.showwarning("Внимание", "Введите название города!")
        return

    status_var.set(f"Загрузка данных для города '{city}'...")
    search_btn.config(state = tk.DISABLED)
    winmain.update()

    weather_data = get_weather(city)

    if weather_data:
        update_display(weather_data)
        status_var.set(f"Данные для города '{city}' обновлены")
    else:
        status_var.set("Ошибка загрузки данных")

    search_btn.config(state = tk.NORMAL)


# Функция быстрого выбора города
def quick_select(city):
    city_entry.delete(0, tk.END)
    city_entry.insert(0, city)
    search_weather()


# ------------------ GUI ------------------


# Создание окна
winmain = tk.Tk()
winmain.title("Погода")
winmain.geometry("700x700")
winmain.resizable(False, False)

# Основной фрейм
main_frame = ttk.Frame(winmain, padding = "15")
main_frame.pack(fill = "both", expand = True)

# Первая строка: поле ввода города, кнопка поиска, кнопка настроек
row_frame = ttk.Frame(main_frame)
row_frame.grid(row = 0, column = 0, columnspan = 4, sticky = "ew", pady = (0, 10))

ttk.Label(row_frame, text = "Название города:", font = ("Segoe UI", 11)).pack(side = "left")

city_entry = ttk.Entry(row_frame, font = ("Segoe UI", 11), width = 25)
city_entry.pack(side = "left", padx = (10, 10))
city_entry.bind("<Return>", lambda event: search_weather())

search_btn = ttk.Button(row_frame, text = "Поиск", command = search_weather, width = 10)
search_btn.pack(side = "left", padx = (0, 10))

settings_btn = ttk.Button(row_frame, text = "Key API", command = open_settings, width = 10)
settings_btn.pack(side = "left")

# Рамка для отображения погоды
weather_frame = ttk.LabelFrame(main_frame, text = "Погода", padding = "15")
weather_frame.grid(row = 1, column = 0, columnspan = 4, pady = 15, sticky = "nsew")

# Фрейм для иконки и температуры
icon_temp_frame = ttk.Frame(weather_frame)
icon_temp_frame.pack(fill = "x", pady = (0, 10))

# Метка для иконки
icon_label = ttk.Label(icon_temp_frame, text = "")
icon_label.pack(side = "left", padx = (0, 20))

# Фрейм для температуры
temp_frame = ttk.Frame(icon_temp_frame)
temp_frame.pack(side = "left", fill = "both", expand = True)

temp_label = ttk.Label(
    temp_frame,
    text = "--°C",
    font = ("Segoe UI", 32, "bold")
)
temp_label.pack(anchor = "w")

feels_label = ttk.Label(
    temp_frame,
    text = "Ощущается: --°C",
    font = ("Segoe UI", 11)
)
feels_label.pack(anchor = "w", pady = (5, 0))

description_label = ttk.Label(
    temp_frame,
    text = "",
    font = ("Segoe UI", 12)
)
description_label.pack(anchor = "w", pady = (5, 0))

# Разделитель
ttk.Separator(weather_frame, orient = "horizontal").pack(fill = "x", pady = 10)

# Дополнительная информация
info_frame = ttk.Frame(weather_frame)
info_frame.pack(fill = "x")

# Левая колонка
left_info = ttk.Frame(info_frame)
left_info.pack(side = "left", fill = "both", expand = True)

ttk.Label(left_info, text = "🌡️ Давление:", font = ("Segoe UI", 10)).pack(anchor = "w", pady = 2)
pressure_label = ttk.Label(left_info, text = "-- мм рт. ст.", font = ("Segoe UI", 10))
pressure_label.pack(anchor = "w", pady = (0, 8))

ttk.Label(left_info, text = "💧 Влажность:", font = ("Segoe UI", 10)).pack(anchor = "w", pady = 2)
humidity_label = ttk.Label(left_info, text = "--%", font = ("Segoe UI", 10))
humidity_label.pack(anchor = "w", pady = (0, 8))

ttk.Label(left_info, text = "🌫️ Видимость:", font = ("Segoe UI", 10)).pack(anchor = "w", pady = 2)
visibility_label = ttk.Label(left_info, text = "-- км", font = ("Segoe UI", 10))
visibility_label.pack(anchor = "w", pady = (0, 8))

# Правая колонка
right_info = ttk.Frame(info_frame)
right_info.pack(side = "right", fill = "both", expand = True)

ttk.Label(right_info, text = "🌬️ Ветер:", font = ("Segoe UI", 10)).pack(anchor = "w", pady = 2)
wind_label = ttk.Label(right_info, text = "-- м/с", font = ("Segoe UI", 10))
wind_label.pack(anchor = "w", pady = (0, 8))

ttk.Label(right_info, text = "🧭 Направление:", font = ("Segoe UI", 10)).pack(anchor = "w", pady = 2)
wind_dir_label = ttk.Label(right_info, text = "--", font = ("Segoe UI", 10))
wind_dir_label.pack(anchor = "w", pady = (0, 8))

ttk.Label(right_info, text = "☁️ Облачность:", font = ("Segoe UI", 10)).pack(anchor = "w", pady = 2)
clouds_label = ttk.Label(right_info, text = "--%", font = ("Segoe UI", 10))
clouds_label.pack(anchor = "w", pady = (0, 8))

# Солнце
sun_frame = ttk.Frame(weather_frame)
sun_frame.pack(fill = "x", pady = (10, 0))

ttk.Label(sun_frame, text = "🌅 Рассвет:", font = ("Segoe UI", 10)).pack(side = "left", padx = (0, 10))
sunrise_label = ttk.Label(sun_frame, text = "--:--", font = ("Segoe UI", 10))
sunrise_label.pack(side = "left", padx = (0, 20))

ttk.Label(sun_frame, text = "🌇 Закат:", font = ("Segoe UI", 10)).pack(side = "left", padx = (0, 10))
sunset_label = ttk.Label(sun_frame, text = "--:--", font = ("Segoe UI", 10))
sunset_label.pack(side = "left")

# Рамка с городами по умолчанию
cities_frame = ttk.LabelFrame(main_frame, text = "Быстрый выбор", padding = "10")
cities_frame.grid(row = 2, column = 0, columnspan = 4, pady = 10, sticky = "nsew")

# Кнопки городов в ряд
cities_buttons_frame = ttk.Frame(cities_frame)
cities_buttons_frame.pack(fill = "x")

for i, city_main in enumerate(DEFAULT_CITIES):
    btn = ttk.Button(
        cities_buttons_frame,
        text = city_main,
        command = lambda c = city_main: quick_select(c),
        width = 15
    )
    btn.pack(side = "left", padx = 5, pady = 3)

# Статус бар
status_var = tk.StringVar()
status_var.set("Готов к работе. Введите API ключ в настройках.")
status_bar = ttk.Label(
    winmain,
    textvariable = status_var,
    relief = "sunken",
    anchor = "w",
    padding = (5, 2)
)
status_bar.pack(side = "bottom", fill = "x")
main_frame.columnconfigure(0, weight = 1)
main_frame.rowconfigure(1, weight = 1)

# Запуск
winmain.mainloop()