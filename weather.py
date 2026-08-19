"""
Weather Lookup Tool — Pleximus Hackathon 

External API call + response parsing, using Open-Meteo. tkinter popup window.

Run: python weather_gui.py
"""

import requests
import tkinter as tk
from tkinter import font as tkfont

KNOWN_CITIES = {
    "mumbai": (19.07, 72.87),
    "ratnagiri": (16.99, 73.31),
    "delhi": (28.61, 77.21),
    "bangalore": (12.97, 77.59),
    "pune": (18.52, 73.86),
    "new york": (40.71, -74.01),
    "london": (51.51, -0.13),
}


def get_weather(latitude: float, longitude: float) -> dict:
    """Same core logic as the terminal version — call Open-Meteo and parse the result."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": latitude, "longitude": longitude, "current_weather": "true"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print("RAW RESPONSE:", data)  # keep logging raw JSON for debugging

        current = data.get("current_weather")
        if not current:
            return {"ok": False, "error": "No 'current_weather' field in response"}

        return {
            "ok": True,
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "weather_code": current.get("weathercode"),
            "time": current.get("time"),
        }
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Request timed out — check your internet connection"}
    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": f"Weather API request failed: {e}"}


def get_weather_by_city(city_name: str) -> dict:
    key = city_name.strip().lower()
    if key not in KNOWN_CITIES:
        return {"ok": False, "error": f"Unknown city '{city_name}'. Try: {', '.join(KNOWN_CITIES)}"}
    lat, lon = KNOWN_CITIES[key]
    return get_weather(lat, lon)


# --- GUI ---------------------------------------------------------------

class WeatherApp:
    def __init__(self, root):
        self.root = root
        root.title("Hackathon Weather Lookup")
        root.geometry("340x380")
        root.resizable(False, False)
        root.configure(bg="#1e1e2e")

        label_font = tkfont.Font(size=11)
        input_font = tkfont.Font(size=14)
        result_font = tkfont.Font(size=13)

        tk.Label(
            root, text="Enter a city:", font=label_font, bg="#1e1e2e", fg="white"
        ).pack(pady=(20, 5))

        self.city_var = tk.StringVar()
        entry = tk.Entry(
            root, textvariable=self.city_var, font=input_font, justify="center",
            bd=0, bg="#2a2a3d", fg="white", insertbackground="white",
        )
        entry.pack(pady=5, ipady=8, padx=30, fill="x")
        entry.bind("<Return>", lambda event: self.lookup())
        entry.focus()

        hint = ", ".join(KNOWN_CITIES)
        tk.Label(
            root, text=f"Known: {hint}", font=("Segoe UI", 8), bg="#1e1e2e",
            fg="#888", wraplength=280, justify="center",
        ).pack(pady=(2, 10))

        tk.Button(
            root, text="Get Weather", font=label_font, bd=0, bg="#f5a623", fg="white",
            activebackground="#e0951c", command=self.lookup,
        ).pack(pady=5, ipadx=10, ipady=6)

        self.result_label = tk.Label(
            root, text="", font=result_font, bg="#1e1e2e", fg="#7ee787",
            justify="left", wraplength=300,
        )
        self.result_label.pack(pady=20, padx=20)

    def lookup(self):
        city = self.city_var.get().strip()
        if not city:
            return
        self.result_label.config(text="Loading...", fg="#f5a623")
        self.root.update_idletasks()  # refresh UI before the (blocking) network call

        result = get_weather_by_city(city)

        if result["ok"]:
            text = (
                f"{city.title()}\n"
                f"Temperature: {result['temperature_c']}°C\n"
                f"Wind speed: {result['windspeed_kmh']} km/h\n"
                f"Time: {result['time']}"
            )
            self.result_label.config(text=text, fg="#7ee787")
        else:
            self.result_label.config(text=f"Error: {result['error']}", fg="#ff6b6b")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()