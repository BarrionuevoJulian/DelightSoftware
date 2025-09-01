import requests
print(requests.__version__)

# Reemplazá con tus claves reales
API_KEYS = {
    "openweathermap": "cd783741cebaecad197c420ca516e3dd",
    "weatherapi": "TU_API_KEY_WEATHERAPI",
    "visualcrossing": "TU_API_KEY_VISUALCROSSING"
}

CIUDAD = "Buenos Aires"

def obtener_openweathermap(ciudad):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEYS['openweathermap']}&units=metric"
    r = requests.get(url).json()
    return {
        "fuente": "OpenWeatherMap",
        "ciudad": r["name"],
        "pais": r["sys"]["country"],
        "viento_velocidad": r["wind"]["speed"],
        "viento_direccion": r["wind"].get("deg", "N/A")
    }

def obtener_weatherapi(ciudad):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEYS['weatherapi']}&q={ciudad}"
    r = requests.get(url).json()
    return {
        "fuente": "WeatherAPI",
        "ciudad": r["location"]["name"],
        "pais": r["location"]["country"],
        "viento_velocidad": r["current"]["wind_kph"],
        "viento_direccion": r["current"]["wind_degree"]
    }

def obtener_visualcrossing(ciudad):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{ciudad}/today?unitGroup=metric&include=current&key={API_KEYS['visualcrossing']}&contentType=json"
    r = requests.get(url).json()
    viento = r["currentConditions"]
    return {
        "fuente": "Visual Crossing",
        "ciudad": r["resolvedAddress"],
        "pais": "N/A",
        "viento_velocidad": viento["windspeed"],
        "viento_direccion": viento["winddir"]
    }

# Ejecutar consultas
datos = [
    obtener_openweathermap(CIUDAD)
    #obtener_weatherapi(CIUDAD),
    #obtener_visualcrossing(CIUDAD)
]

# Mostrar resultados
for d in datos:
    print(f"\n🌐 Fuente: {d['fuente']}")
    print(f"📍 Ciudad: {d['ciudad']} ({d['pais']})")
    print(f"🌬 Velocidad del viento: {d['viento_velocidad']} km/h")
    print(f"🧭 Dirección del viento: {d['viento_direccion']}°")
