# task4.2

import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io

# Константы
CAT_API_URL = "https://api.thecatapi.com/v1/images/search"
DOG_API_URL = "https://dog.ceo/api/breeds/image/random"


# ------------------ Логика ------------------


def get_cat_image():
    try:
        response = requests.get(CAT_API_URL, timeout = 10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]["url"]

        return None
    except requests.exceptions.RequestException:
        return None


def get_dog_image():
    try:
        response = requests.get(DOG_API_URL, timeout = 10)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["message"]

        return None
    except requests.exceptions.RequestException:
        return None


def load_image_from_url(url):
    try:
        response = requests.get(url, timeout = 10)
        if response.status_code == 200:
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img.thumbnail((400, 300), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)

        return None
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None


def on_cat_button():
    status_var.set("Загрузка кота...")
    cat_btn.config(state = tk.DISABLED)
    dog_btn.config(state = tk.DISABLED)
    winmain.update()
    image_url = get_cat_image()
    if image_url:
        photo = load_image_from_url(image_url)
        if photo:
            image_label.config(image = photo)
            image_label.image = photo
            status_var.set("Кот загружен !")
        else:
            image_label.config(image = "")
            image_label.image = None
            status_var.set("Ошибка загрузки кота")
    else:
        image_label.config(image = "")
        image_label.image = None
        status_var.set("Не удалось получить кота")
    cat_btn.config(state = tk.NORMAL)
    dog_btn.config(state = tk.NORMAL)


def on_dog_button():
    status_var.set("Загрузка собаки...")
    cat_btn.config(state = tk.DISABLED)
    dog_btn.config(state = tk.DISABLED)
    winmain.update()
    image_url = get_dog_image()
    if image_url:
        photo = load_image_from_url(image_url)
        if photo:
            image_label.config(image = photo)
            image_label.image = photo
            status_var.set("Собака загружена!")
        else:
            image_label.config(image = "")
            image_label.image = None
            status_var.set("Ошибка загрузки собаки")
    else:
        image_label.config(image = "")
        image_label.image = None
        status_var.set("Не удалось получить собаку")
    cat_btn.config(state = tk.NORMAL)
    dog_btn.config(state = tk.NORMAL)


# ------------------ GUI ------------------


winmain = tk.Tk()
winmain.title("Random Cat and Dog")
winmain.geometry("600x600")
winmain.resizable(False, False)
main_frame = ttk.Frame(winmain, padding = "15")
main_frame.pack(fill = "both", expand = True)

# Кнопки
button_frame = ttk.Frame(main_frame)
button_frame.grid(row = 1, column = 0, columnspan = 2, pady = 10)

cat_btn = ttk.Button(
    button_frame,
    text = "Получить кота",
    command = on_cat_button,
    width = 20
)
cat_btn.pack(side = "left", padx = 10)
dog_btn = ttk.Button(
    button_frame,
    text = "Получить собаку",
    command = on_dog_button,
    width = 20
)
dog_btn.pack(side = "left", padx = 10)

# Рамка для изображения
image_frame = ttk.LabelFrame(main_frame, text = "Изображение", padding = "10")
image_frame.grid(row = 2, column = 0, columnspan = 2, pady = 10, sticky = "nsew")

image_label = ttk.Label(image_frame, text = "Нажмите кнопку для получения фото", background = "white")
image_label.pack(fill = "both", expand = True, padx = 5, pady = 5)

# Статус бар
status_var = tk.StringVar()
status_var.set("Готов к работе.")
status_bar = ttk.Label(
    winmain,
    textvariable = status_var,
    relief = "sunken",
    anchor = "w",
    padding = (5, 2)
)
status_bar.pack(side = "bottom", fill = "x")
main_frame.columnconfigure(0, weight = 1)
main_frame.rowconfigure(2, weight = 1)
winmain.mainloop()