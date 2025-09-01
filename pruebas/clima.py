import time
import requests
import serial
import json

# Configurar UART
ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)

API_KEY = "cd783741cebaecad197c420ca516e3dd"
CIUDAD = "Buenos Aires"

def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def obtener_openweathermap(ciudad):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=15).json()
        return {
            "viento_velocidad": r["wind"]["speed"],
            "viento_direccion": r["wind"].get("deg", 0)
        }
    except Exception as e:
        print("? Error al obtener datos:", e)
        return None

def main():
    print("?? Control WLED con viento usando segmentos (Ctrl+C para salir)...\n")
    try:
        while True:
            data = obtener_openweathermap(CIUDAD)
            if data:
                vel = data['viento_velocidad']
                dir = data['viento_direccion']

                ix = map_range(vel, 0, 20, 0, 255)
                sx = map_range(dir, 0, 360, 0, 255)

                comando = {"seg": [{"ix": ix,"sx": sx}]}

                json_cmd = json.dumps(comando)
                ser.write((json_cmd + '\r').encode())

                print(f"Vel: {vel:.2f} m/s | ix: {ix} ---- Dir: {dir} | sx: {sx}")
            else:
                print("No se pudo obtener datos del clima.")
            time.sleep(15)
    except KeyboardInterrupt:
        print("\n Finalizado por el usuario.")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
