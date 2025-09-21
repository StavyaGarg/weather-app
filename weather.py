from tkinter import *
import tkinter as tk
from tkinter import messagebox
from geopy.geocoders import Nominatim
from PIL import Image, ImageTk
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import requests

root = Tk()
root.title("Weather App")
root.geometry("890x470+300+180")
root.configure(bg="#53a7f6")
root.resizable(False, False)

# ---------------- Weather code mapping ----------------
weather_map = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    95: "Thunderstorm",
    96: "Thunderstorm w/ hail",
    99: "Thunderstorm w/ heavy hail"
}

# Weather icons mapping
icons = {
    "ClearDay": "img/sun.png",
    "ClearNight": "img/moon.png",
    "Cloudy": "img/partlycloudy.png",
    "Overcast": "img/overcast.png",
    "Rain": "img/rain.png",
    "Snow": "img/snow.png",
    "Thunder": "img/thunder.png",
    "Fog": "img/fog.png",
    "Unknown": "img/unknown.png"
}

def get_icon_for_weather(code, is_day):
    if code == 0:
        return icons["ClearDay"] if is_day == 1 else icons["ClearNight"]
    elif code in [1, 2]:
        return icons["Cloudy"]
    elif code == 3:
        return icons["Overcast"]
    elif code in [61, 63, 65, 51, 53, 55]:
        return icons["Rain"]
    elif code in [71, 73, 75]:
        return icons["Snow"]
    elif code in [95, 96, 99]:
        return icons["Thunder"]
    elif code in [45, 48]:
        return icons["Fog"]
    else:
        return icons["Unknown"]

# ---------------- Get Weather ----------------
def getWeather():
    try:
        city = text_enter.get()

        geolocator = Nominatim(user_agent="geoapiExcercise")
        location = geolocator.geocode(city)
        if not location:
            messagebox.showerror("Error", "City not found!")
            return

        obj = TimezoneFinder()
        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
        timezone.config(text=result)

        home = pytz.timezone(result)
        local_time = datetime.now(home)
        time = local_time.strftime("%I:%M %p")
        clock.config(text=time)

        # API request
        url = f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,weather_code,is_day&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=7"
        resp = requests.get(url)
        data = resp.json()

        # Current weather
        temp = data['current']['temperature_2m']
        humidity = data['current']['relative_humidity_2m']
        pressure = data['current']['surface_pressure']
        wind = data['current']['wind_speed_10m']
        weather_code = data['current']['weather_code']
        is_day = data['current']['is_day']

        description = weather_map.get(weather_code, "Unknown")

        t1.config(text=f"{temp} °C")
        t2.config(text=f"{humidity} %")
        t3.config(text=f"{pressure} hPa")
        t4.config(text=f"{wind} m/s")
        t5.config(text=description)

        # ---- Daily forecast ----
        dates = data['daily']['time']
        tmax = data['daily']['temperature_2m_max']
        tmin = data['daily']['temperature_2m_min']
        codes = data['daily']['weather_code']

        for i in range(7):
            day_obj = datetime.strptime(dates[i], "%Y-%m-%d")
            days_labels[i].config(text=day_obj.strftime("%A"))
            cond = weather_map.get(codes[i], f"Code {codes[i]}")
            temps_labels[i].config(text=f"Max:{tmax[i]}°C\nMin:{tmin[i]}°C\n{cond}")

            # Forecast icon (daytime icons)
            icon_path = get_icon_for_weather(codes[i], 1)
            img = Image.open(icon_path)
            img = img.resize((50, 50), Image.Resampling.LANCZOS)
            icon_img = ImageTk.PhotoImage(img)
            icons_labels[i].config(image=icon_img)
            icons_labels[i].image = icon_img

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- UI ----------------
logo = PhotoImage(file="img/logo.png")
root.iconphoto(False, logo)

# Boxes and Labels
box1 = PhotoImage(file="img/rect1.png")
Label(root, image=box1, bg="#53a7f6").place(x=30, y=110)

Label(root,text="Temperature",font=('Helvetica',11),fg="white",bg="#203243").place(x=50,y=120)
Label(root,text="Humidity",font=('Helvetica',11),fg="white",bg="#203243").place(x=50,y=140)
Label(root,text="Pressure",font=('Helvetica',11),fg="white",bg="#203243").place(x=50,y=160)
Label(root,text="Wind Speed",font=('Helvetica',11),fg="white",bg="#203243").place(x=50,y=180)
Label(root,text="Description",font=('Helvetica',11),fg="white",bg="#203243").place(x=50,y=200)

search=PhotoImage(file="img/rect3.png")
Label(root, image=search, bg="#53a7f6").place(x=270, y=120)

text_enter = tk.Entry(root,justify='center',width=15,font=('Arial',25,'bold'),bg='#203243',border=0,fg="white")
text_enter.place(x=370,y=130)
text_enter.focus()

s_icon=PhotoImage(file='img/l6.png')
Button(image=s_icon,borderwidth=0,cursor="hand2",bg="#203243",activebackground="#203243",command=getWeather).place(x=645,y=125)

frame = Frame(root, width=900, height=180, bg="#212120")
frame.pack(side=BOTTOM)

clock=Label(root,font=("Helvetica",30),fg='white',bg="#53a7f6")
clock.place(x=30,y=20)
timezone=Label(root,font=("Helvetica",20),fg='white',bg="#53a7f6")
timezone.place(x=650,y=20)

t1=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t1.place(x=150,y=120)
t2=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t2.place(x=150,y=140)
t3=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t3.place(x=150,y=160)
t4=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t4.place(x=150,y=180)
t5=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t5.place(x=150,y=200)

# ----------------- 7-Day Forecast Frames -----------------
forecast_frames = []
days_labels = []
temps_labels = []
icons_labels = []

x_positions = [35, 305, 405, 505, 605, 705, 805]

for i in range(7):
    frame = Frame(root,width=70 if i!=0 else 230,height=115 if i!=0 else 132,bg="#282829")
    frame.place(x=x_positions[i], y=315)
    forecast_frames.append(frame)

    day_label = Label(frame,font="arial 12 bold" if i==0 else "arial 8 bold",bg="#282829",fg="#fff")
    day_label.place(x=60 if i==0 else 9, y=5)
    days_labels.append(day_label)

    temp_label = Label(frame,bg="#282829",fg="#53a7f6" if i==0 else "#fff",font="arial 11 bold" if i==0 else "arial 7")
    temp_label.place(x=20 if i==0 else 5, y=50 if i==0 else 30)
    temps_labels.append(temp_label)

    icon_label = Label(frame,bg="#282829")
    icon_label.place(x=5, y=70 if i==0 else 50)
    icons_labels.append(icon_label)

# Assign forecast labels to global names used in getWeather()
d1, d2, d3, d4, d5, d6, d7 = days_labels
d1temp, d2temp, d3temp, d4temp, d5temp, d6temp, d7temp = temps_labels
d1icon, d2icon, d3icon, d4icon, d5icon, d6icon, d7icon = icons_labels

root.mainloop()
