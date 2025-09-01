import time
import json
from datetime import datetime
import serial
from pico import VoiceProcessor
from sensor import PresenciaSensor
from clima import obtener_datos, map_range

# -------- CONFIGURACIÓN GLOBAL --------
ACCESS_KEY = "O7D9uT2joAvNPwbyExhfvMMGy9ki6AtTi2YhgJn9bGaCqoo9+sXNeA=="
AUDIO_DEVICE_INDEX = 1
CIUDAD = "Buenos Aires"
API_KEY = "cd783741cebaecad197c420ca516e3dd"

CLIMA_INTERVAL = 60         # segundos
DETECCION_INTERVAL = 1      # segundos

# -------- INICIALIZACIÓN --------
voz = VoiceProcessor(ACCESS_KEY, AUDIO_DEVICE_INDEX)
voz.iniciar_serial('/dev/ttyUSB0')
voz.iniciar_porcu_rhino()

sensor = PresenciaSensor()
sensor.configurar()

ultima_actualizacion_clima = 0
ultimo_chequeo_presencia = 0
datos_clima = None
radarTrue = True

serial.Serial(port='/dev/ttySerial0', baudrate=115200, timeout=1)

print("\nIniciando monitoreo. Ctrl+C para salir.\n")

try:
    while True:
        ahora = time.time()
        voz.correr()

        # --- CLIMA ---
        if ahora - ultima_actualizacion_clima >= CLIMA_INTERVAL:
            datos_clima = obtener_datos(API_KEY, CIUDAD)
            if datos_clima:
                vel = datos_clima['viento_velocidad']
                dir = datos_clima['viento_direccion']
                ix = map_range(vel, 0, 20, 0, 255)
                sx = map_range(dir, 0, 360, 0, 255)
            else:
                print("[CLIMA] No se pudo obtener datos del clima.")
                vel, dir, ix, sx = 125, 125, 0, 0

            comando = {"seg": [{"ix": ix, "sx": sx}]}
            voz.ser.write((json.dumps(comando) + '\r').encode())
            print(f"[CLIMA] Vel: {vel:.2f} m/s (ix: {ix}) | Dir: {dir}° (sx: {sx})")
            ultima_actualizacion_clima = ahora

        # --- DETECCIÓN ---
        if ahora - ultimo_chequeo_presencia >= DETECCION_INTERVAL:
            if sensor.detectar_movimiento():
                print("[DETECCIÓN] Movimiento detectado -> Enviando comando preset.")
                if radarTrue:
                    voz.ser.write('{"ps":10}\r'.encode())
                    print("-- Iluminacion activada --")
                    radarTrue = False
            else:
                radarTrue = True
                print(" Sin presencia ")
            ultimo_chequeo_presencia = ahora

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nPrograma finalizado por el usuario.")

finally:
    voz.cerrar()
