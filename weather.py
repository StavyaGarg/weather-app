from tkinter import *
from tkinter import messagebox
from geopy.geocoders import Nominatim
from PIL import Image, ImageTk
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import requests
import threading

root = Tk()
root.title("Weather App")
root.geometry("860x490+300+180")
root.configure(bg="#53a7f6")
root.resizable(False, False)

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
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain",
    81: "Moderate rain",
    82: "Violent rain",
    85: "Slight snow",
    86: "Heavy snow ",
    95: "Thunderstorm",
    96: "Thunderstorm w/ hail",
    99: "Thunderstorm w/ heavy hail"
}

icons = {
    "ClearDay": "img/sun.png",
    "ClearNight": "img/moon.png",
    "Cloudy": "img/partlycloudy.png",
    "Overcast": "img/overcast.png",
    "Rain": "img/rain.png",
    "Snow": "img/snow.png",
    "Thunder": "img/thunder.png",
    "Fog": "img/fog.png",
}

recent_searches_menu = None
recent_searches = []

def get_icon_for_weather(code, is_day):
    if code == 0:
        return icons["ClearDay"] if is_day == 1 else icons["ClearNight"]
    elif code in [1, 2]:
        return icons["Cloudy"]
    elif code == 3:
        return icons["Overcast"]
    elif code in [45, 48]:
        return icons["Fog"]
    elif code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        return icons["Rain"]
    elif code in [71, 73, 75, 77, 85, 86]:
        return icons["Snow"]
    elif code in [95,96, 99]:
        return icons["Thunder"]


def show_recent_searches_menu(event):
    global recent_searches_menu
    if recent_searches_menu:
        recent_searches_menu.destroy()

    if not recent_searches:
        return

    recent_searches_menu = Toplevel(root)
    recent_searches_menu.overrideredirect(True) 
    
    x = text_enter.winfo_rootx()
    y = text_enter.winfo_rooty() + text_enter.winfo_height() + 5
    recent_searches_menu.geometry(f"+{x+150}+{y+5}")

    menu_frame = Frame(recent_searches_menu, bg="#203243")
    menu_frame.pack(fill="both", expand=True)

    title_label = Label(menu_frame, text="Recent Searches", font=("Arial", 10, "bold"), bg="#203243", fg="white", pady=5)
    title_label.pack(fill="x", padx=5)
    
    separator = Frame(menu_frame, height=2, bd=1, relief="sunken", bg="#53a7f6")
    separator.pack(fill="x", padx=5, pady=2)

    for city in recent_searches:
        item = Label(menu_frame, text=city, font=("Arial", 10), bg="#203243", fg="white", padx=10, pady=5, cursor="hand2")
        item.pack(fill="x", pady=2)
        item.bind("<Button-1>", lambda e, city_name=city: select_recent_search(city_name))
    
    recent_searches_menu.bind("<FocusOut>", hide_recent_searches_menu)
    recent_searches_menu.focus_set()

def hide_recent_searches_menu(event=None):
    global recent_searches_menu
    if recent_searches_menu:
        recent_searches_menu.destroy()
        recent_searches_menu = None

def select_recent_search(city):
    text_enter.delete(0, END)
    text_enter.insert(0, city)
    hide_recent_searches_menu()
    thread_weather()

def get_weather():
    try:
        city = text_enter.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name.")
            return

        if city not in recent_searches:
            recent_searches.insert(0, city)
            if len(recent_searches) > 5:
                recent_searches.pop()

        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(city)
        if not location:
            messagebox.showerror("Error", "City not found.")
            return

        obj = TimezoneFinder()
        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
        timezone.config(text=result)

        home = pytz.timezone(result)
        local_time = datetime.now(home)
        time = local_time.strftime("%I:%M %p")
        clock.config(text=time)

        url = f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,weather_code,is_day&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=7"
        resp = requests.get(url)
        data = resp.json()

        temp = data['current']['temperature_2m']
        humidity = data['current']['relative_humidity_2m']
        pressure = data['current']['surface_pressure']
        wind = data['current']['wind_speed_10m']
        weather_code = data['current']['weather_code']
        is_day = data['current']['is_day']

        description = weather_map.get(weather_code, f"Code {weather_code}")

        t1.config(text=f"{temp} °C")
        t2.config(text=f"{humidity} %")
        t3.config(text=f"{pressure} hPa")
        t4.config(text=f"{wind} m/s")
        t5.config(text=description)

        dates = data['daily']['time']
        tmax = data['daily']['temperature_2m_max']
        tmin = data['daily']['temperature_2m_min']
        codes = data['daily']['weather_code']

        for i in range(7):
            if i == 0:
                days_labels[i].config(text="Today")
            else:
                day_obj = datetime.strptime(dates[i], "%Y-%m-%d")
                days_labels[i].config(text=day_obj.strftime("%A"))

            cond = weather_map.get(codes[i], f"Code {codes[i]}")
            temps_labels[i].config(text=f"Max:{tmax[i]}°C\nMin:{tmin[i]}°C\n{cond}")

            icon_path = get_icon_for_weather(codes[i], 1)
            if icon_path:
                img = Image.open(icon_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                icon_img = ImageTk.PhotoImage(img)
                icons_labels[i].config(image=icon_img)
                icons_labels[i].image = icon_img
    except Exception as e:
        messagebox.showerror("Error", str(e))

def thread_weather():
    threading.Thread(target=get_weather).start()

try:
    logo = PhotoImage(file="img/logo.png")
    root.iconphoto(False, logo)

    img_rect1 = Image.open("img/rect1.png")
    resized_img_rect1 = img_rect1.resize((img_rect1.width + 50, img_rect1.height + 15), Image.Resampling.LANCZOS)
    box1 = ImageTk.PhotoImage(resized_img_rect1)
    Label(root, image=box1, bg="#53a7f6").place(x=50, y=110)

    search=PhotoImage(file="img/rect3.png")
    Label(root, image=search, bg="#53a7f6").place(x=300, y=120)
    s_icon=PhotoImage(file='img/l6.png')
except TclError:
    messagebox.showerror("File Not Found", "Please ensure 'img/logo.png', 'img/rect1.png', 'img/rect3.png', and 'img/l6.png' exist in an 'img' folder.")
    root.destroy()
    exit()

Label(root,text="Temperature",font=('Helvetica',11),fg="white",bg="#203243").place(x=60,y=120)
Label(root,text="Humidity",font=('Helvetica',11),fg="white",bg="#203243").place(x=60,y=140)
Label(root,text="Pressure",font=('Helvetica',11),fg="white",bg="#203243").place(x=60,y=160)
Label(root,text="Wind Speed",font=('Helvetica',11),fg="white",bg="#203243").place(x=60,y=180)
Label(root,text="Description",font=('Helvetica',11),fg="white",bg="#203243").place(x=60,y=200)

text_enter = Entry(root,justify='center',width=15,font=('Arial',25,'bold'),bg='#203243',border=0,fg="white")
text_enter.place(x=370,y=130)
text_enter.focus()

text_enter.bind("<Enter>", show_recent_searches_menu)

Button(image=s_icon,borderwidth=0,cursor="hand2",bg="#203243",activebackground="#203243",command=thread_weather).place(x=675,y=125)

frame = Frame(root, width=900, height=180, bg="#212120")
frame.pack(side=BOTTOM)

clock=Label(root,font=("Helvetica",30),fg='white',bg="#53a7f6")
clock.place(x=30,y=20)
timezone=Label(root,font=("Helvetica",20),fg='white',bg="#53a7f6")
timezone.place(x=650,y=20)

t1=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t1.place(x=190,y=120)
t2=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t2.place(x=190,y=140)
t3=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t3.place(x=190,y=160)
t4=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t4.place(x=190,y=180)
t5=Label(root,font=("Helvetica",11),fg="white",bg="#203243")
t5.place(x=190,y=200)

forecast_frames = []
days_labels = []
temps_labels = []
icons_labels = []

box_width = 100
box_height = 145
gap = 15
x_positions = [30, 30 + box_width + gap, 30 + 2*(box_width + gap), 30 + 3*(box_width + gap), 30 + 4*(box_width + gap), 30 + 5*(box_width + gap), 30 + 6*(box_width + gap)]

forecast_y = 335

for i in range(7):
    frame = Frame(root, width=box_width, height=box_height, bg="#282829")
    frame.place(x=x_positions[i], y=forecast_y)
    forecast_frames.append(frame)

    day_label = Label(frame,
                      font="arial 10 bold",
                      bg="#282829",
                      fg="#fff")
    day_label.place(relx=0.5, y=10, anchor=N)
    days_labels.append(day_label)

    temp_label = Label(frame,
                       bg="#282829",
                       fg="#53a7f6",
                       font="arial 8 bold")
    temp_label.place(relx=0.5, y=40, anchor=N)
    temps_labels.append(temp_label)

    icon_label = Label(frame, bg="#282829")
    icon_label.place(relx=0.5, y=90, anchor=N)
    icons_labels.append(icon_label)

root.mainloop()
