from __future__ import print_function
import sys
import os
import time
import json
import requests
import serial
from DFRobot_C4001 import *

# --------- CONFIGURACIÓN ---------
ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
ctype = I2C_MODE  # o UART_MODE

if ctype == I2C_MODE:
    I2C_1 = 0x01
    I2C_ADDR = 0x2A
    radar = DFRobot_C4001_I2C(I2C_1, I2C_ADDR)
else:
    radar = DFRobot_C4001_UART(9600)

API_KEY = "cd783741cebaecad197c420ca516e3dd"
CIUDAD = "Buenos Aires"

def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def obtener_openweathermap(ciudad):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=10).json()
        return {
            "viento_velocidad": r["wind"]["speed"],
            "viento_direccion": r["wind"].get("deg", 0)
        }
    except Exception as e:
        print("[!] Error al obtener datos del clima:", e)
        return None

def setup_sensor():
    print("Inicializando sensor...")
    while not radar.begin():
        print("Sensor initialize failed!!")
        time.sleep(1)

    radar.set_sensor_mode(EXIST_MODE)
    radar.set_detect_thres(11, 100, 11)
    radar.set_detection_range(30, 240, 240)
    radar.set_trig_sensitivity(1)
    radar.set_keep_sensitivity(1)
    radar.set_delay(50, 4)
    radar.set_pwm(50, 0, 10)
    radar.set_io_polaity(1)
    print("Sensor listo.")

# --------- MAIN ---------
def main():
    setup_sensor()
    radarTrue = True  # Para controlar el estado de detección
    clima_interval = 15  # segundos
    deteccion_interval = 1  # segundos

    ultima_actualizacion_clima = 0
    ultimo_chequeo_presencia = 0
    datos_clima = None

    print("\nIniciando monitoreo. Ctrl+C para salir.\n")

    try:
        while True:
            ahora = time.time()

            # Obtener clima cada 15 segundos
            if ahora - ultima_actualizacion_clima >= clima_interval:
                datos_clima = obtener_openweathermap(CIUDAD)
                if datos_clima:
                    vel = datos_clima['viento_velocidad']
                    dir = datos_clima['viento_direccion']
                    ix = map_range(vel, 0, 20, 0, 255)
                    sx = map_range(dir, 0, 360, 0, 255)

                    comando = {"seg": [{"ix": ix, "sx": sx}]}
                    json_cmd = json.dumps(comando)
                    ser.write((json_cmd + '\r').encode())

                    print(f"[CLIMA] Vel: {vel:.2f} m/s (ix: {ix}) | Dir: {dir}° (sx: {sx})")
                else:
                    print("[CLIMA] No se pudo obtener datos del clima.")
                ultima_actualizacion_clima = ahora

            # Chequear detección cada 1 segundo
            if ahora - ultimo_chequeo_presencia >= deteccion_interval:
                if radar.motion_detection() == 1:
                    print("[DETECCIÓN] Movimiento detectado -> Enviando comando preset.")
                    if radarTrue:
                        ser.write(b'{"ps":10}\r')
                        print("-- Iluminacion activada --")
                        radarTrue = False
                else:
                    radarTrue = True
                    print("[DETECCIÓN] Sin presencia.")
                ultimo_chequeo_presencia = ahora

            time.sleep(0.1)  # evitar uso excesivo de CPU

    except KeyboardInterrupt:
        print("\n[!] Programa finalizado por el usuario.")
    finally:
        ser.close()

if __name__ == "__main__":
    main()