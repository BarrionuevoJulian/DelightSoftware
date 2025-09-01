import requests

def obtener_datos(api_key, ciudad):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric"
    try:
        r = requests.get(url, timeout=10).json()
        return {
            "viento_velocidad": r["wind"]["speed"],
            "viento_direccion": r["wind"].get("deg", 0)
        }
    except Exception as e:
        print("[!] Error al obtener datos del clima:", e)
        return None

def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
