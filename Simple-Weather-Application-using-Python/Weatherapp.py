import mysql.connector
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from datetime import datetime
import webbrowser
import urllib.parse
import re

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Lathika143143",
    database="mydatabase"
)
mycursor = db.cursor()

last_checked_time = None

def validate_location(location):
    if re.match("^[a-zA-Z\s,]+$", location):
        return True
    return False

def get_weather(location):
    global last_checked_time

    api_key = "f6be5906359d00480b0462d14341e197"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={location}&units=metric"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        if data["cod"] != "404":
            main = data["main"]
            weather = data["weather"][0]
            temperature = main["temp"]
            humidity = main["humidity"]
            pressure = main["pressure"]
            weather_description = weather["description"]
            rain = data.get("rain", {}).get("1h", 0)

            try:
                mycursor.execute("""
                    INSERT INTO climate (City, Temperature, Humidity, Pressure, Description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (location, temperature, humidity, pressure, weather_description))
                db.commit()
                print("Weather data inserted successfully.")
            except mysql.connector.Error as err:
                print(f"Error inserting data: {err}")

            cultivation_advice = "suitable" if 15 <= temperature <= 30 and 40 <= humidity <= 70 else "not suitable"

            last_checked_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            weather_report = (
                f"Weather in {location}:\n"
                f"Last checked: {last_checked_time}\n"
                f"Temperature: {temperature}°C\n"
                f"Humidity: {humidity}%\n"
                f"Pressure: {pressure} hPa\n"
                f"Description: {weather_description.capitalize()}\n"
                f"Rain: {rain} mm\n"
                f"\nIt is {cultivation_advice} to cultivate crops at this time."
            )
        else:
            weather_report = f"Location {location} not found."

    except requests.exceptions.RequestException as e:
        weather_report = f"Error fetching weather data: {e}"

    return weather_report

def check_crop_yield(location):
    weather_report = get_weather(location)
    if "Location not found" not in weather_report and "Error" not in weather_report:
        lines = weather_report.split('\n')
        temp_line = next(line for line in lines if "Temperature:" in line)
        humidity_line = next(line for line in lines if "Humidity:" in line)
        temperature = float(temp_line.split()[1].replace("°C", ""))
        humidity = int(humidity_line.split()[1].replace("%", ""))

        if 20 <= temperature <= 30 and 50 <= humidity <= 70:
            crop_yield_advice = "The current weather conditions are ideal for a high crop yield."
        else:
            crop_yield_advice = "The current weather conditions are not ideal for a high crop yield."
    else:
        crop_yield_advice = "Unable to determine crop yield advice due to incomplete weather data."

    return crop_yield_advice

def show_weather():
    location = location_entry.get()
    if location:
        if validate_location(location):
            weather_report = get_weather(location)
            display_weather(weather_report)
        else:
            messagebox.showwarning("Input Error", "Invalid Location name.")
    else:
        messagebox.showwarning("Input Error", "Please enter a location.")

def show_crop_yield():
    location = location_entry.get()
    if location:
        if validate_location(location):
            crop_yield_advice = check_crop_yield(location)
            messagebox.showinfo("Crop Yield Advice", crop_yield_advice)
        else:
            messagebox.showwarning("Input Error", "Invalid Location name.")
    else:
        messagebox.showwarning("Input Error", "Please enter a location.")

def copy_to_clipboard(weather_report):
    app.clipboard_clear()
    app.clipboard_append(weather_report)
    messagebox.showinfo("Copied", "Weather report copied to clipboard!")

def share_via_whatsapp(weather_report):
    url = f"https://web.whatsapp.com//send?text={urllib.parse.quote(weather_report)}"
    webbrowser.open(url)

def share_via_email(weather_report):
    subject = "Weather Report"
    body = urllib.parse.quote(weather_report)
    url = f"mailto:?subject={urllib.parse.quote(subject)}&body={body}"
    webbrowser.open(url)

def display_weather(weather_report):
    new_window = tk.Toplevel(app)
    new_window.title("Weather Report")
    new_window.attributes('-fullscreen', True)
    new_window.configure(background="#87CEEB")

    frame = ttk.Frame(new_window, padding="10", style="TFrame")
    frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    weather_text = tk.Text(frame, wrap="word", bg="#87CEEB", font=("Arial", 14), relief="flat")
    weather_text.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))
    weather_text.tag_configure("center", justify='center')

    weather_report_with_spaces = "\n\n".join(weather_report.split('\n'))

    weather_text.insert("1.0", weather_report_with_spaces)
    weather_text.tag_configure("city", foreground="black", font=("Arial", 18, "bold"))
    weather_text.tag_configure("temp", foreground="black")
    weather_text.tag_configure("humidity", foreground="black")
    weather_text.tag_configure("pressure", foreground="black")
    weather_text.tag_configure("description", foreground="black", font=("Arial", 14, "bold"))

    lines = weather_report_with_spaces.split('\n\n')
    for i, line in enumerate(lines):
        weather_text.tag_add("center", f"{2*i+1}.0", f"{2*i+1}.end")
        if "Weather in" in line:
            weather_text.tag_add("city", f"{2*i+1}.0", f"{2*i+1}.end")
        elif "Temperature:" in line:
            weather_text.tag_add("temp", f"{2*i+1}.0", f"{2*i+1}.end")
        elif "Humidity:" in line:
            weather_text.tag_add("humidity", f"{2*i+1}.0", f"{2*i+1}.end")
        elif "Pressure:" in line:
            weather_text.tag_add("pressure", f"{2*i+1}.0", f"{2*i+1}.end")
        elif "Description:" in line:
            weather_text.tag_add("description", f"{2*i+1}.0", f"{2*i+1}.end")

    ttk.Label(frame, text=f"Last checked: {last_checked_time}", font=("Arial", 12), background="#87CEEB").grid(row=1, column=0, pady=5, sticky=tk.W)
    ttk.Label(frame, text=f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", font=("Arial", 12), background="#87CEEB").grid(row=2, column=0, pady=5, sticky=tk.W)

    weather_text.config(state=tk.DISABLED)

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=3, column=0, pady=10)

    exit_button = ttk.Button(button_frame, text="Exit", command=new_window.destroy)
    exit_button.grid(row=0, column=0, padx=5)

    share_whatsapp_button = ttk.Button(button_frame, text="Share via WhatsApp", command=lambda: share_via_whatsapp(weather_report))
    share_whatsapp_button.grid(row=0, column=1, padx=5)

    share_email_button = ttk.Button(button_frame, text="Share via Email", command=lambda: share_via_email(weather_report))
    share_email_button.grid(row=0, column=2, padx=5)

def show_frame(frame):
    frame.tkraise()

def check_rain_probability(location):
    weather_report = get_weather(location)
    if "Location not found" not in weather_report and "Error" not in weather_report:
        lines = weather_report.split('\n')
        rain_line = next((line for line in lines if "Rain:" in line), None)
        if rain_line:
            rain_amount = float(rain_line.split()[1])
            if rain_amount > 0:
                rain_probability = "There is a possibility of rain."
            else:
                rain_probability = "No rain expected."
        else:
            rain_probability = "Rain data not available."
    else:
        rain_probability = "Unable to determine rain probability due to incomplete weather data."

    return rain_probability

def show_rain_probability():
    location = location_entry.get()
    if location:
        if validate_location(location):
            rain_probability = check_rain_probability(location)
            messagebox.showinfo("Rain Probability", rain_probability)
        else:
            messagebox.showwarning("Input Error", "Invalid Location name.")
    else:
        messagebox.showwarning("Input Error", "Please enter a location.")

app = ThemedTk(theme="arc")
app.title("Weather App")
app.attributes('-fullscreen', True)
app.configure(background="#87CEEB")

style = ttk.Style(app)
style.configure("TFrame", background="#87CEEB")
style.configure("TLabel", background="#87CEEB", font=("Arial", 14))
style.configure("TButton", font=("Arial", 12), padding=10)
style.configure("TCombobox", font=("Arial", 12))

container = ttk.Frame(app, padding="10", style="TFrame")
container.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

welcome_frame = ttk.Frame(container, padding="20", style="TFrame")
welcome_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

welcome_label = ttk.Label(welcome_frame, text="Welcome to the Weather App!", font=("Arial", 24, "bold"), background="#87CEEB", foreground="navy")
welcome_label.grid(row=0, column=0, padx=10, pady=10)

quote_label = ttk.Label(welcome_frame, text="“Wherever you go, no matter what the weather, always bring your own sunshine.”", font=("Arial", 16, "italic"), background="#87CEEB", foreground="darkgreen")
quote_label.grid(row=1, column=0, padx=10, pady=10)

welcome_button = ttk.Button(welcome_frame, text="Get Started", command=lambda: show_frame(main_frame))
welcome_button.grid(row=2, column=0, pady=20)

main_frame = ttk.Frame(container, padding="20", style="TFrame")
main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

ttk.Label(main_frame, text="Enter location (city, state, country):", background="#87CEEB").grid(row=1, column=0, padx=10, pady=10)

location_entry = ttk.Entry(main_frame, width=50)
location_entry.grid(row=1, column=1, padx=10, pady=10)

ttk.Button(main_frame, text="Get Weather", command=show_weather).grid(row=2, columnspan=2, pady=20)


exit_button_main = ttk.Button(main_frame, text="Exit", command=app.destroy)
exit_button_main.grid(row=3, column=1, padx=10, pady=10)

rain_button = ttk.Button(main_frame, text="Check Rain Probability", command=show_rain_probability)
rain_button.grid(row=4, column=0, columnspan=2, pady=10)

show_frame(welcome_frame)
app.mainloop()

