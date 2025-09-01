import time
import json
from datetime import datetime
import serial
from sensor import PresenciaSensor

# --- CONFIGURACIÓN ---
INTERVALO = 2  # cada cuánto se chequea el sensor

LENTO, RAPIDO = 1, 0.2  # intervalos de espera
CHEQUEOS_REQUERIDOS = 3  # cantidad de lecturas coherentes necesarias
TIEMPO_ESPERA_AUSENCIA = 5  # espera después de confirmar presencia antes de chequear ausencia

sensor = PresenciaSensor(modo='I2C')
sensor.configurar()

ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
ser.write ('{"ps":2}\r'.encode())

# --- ESTADOS ---
estado = "esperando_presencia"
contPresencia = 0
contAusencia = 0
tiempo_confirmacion_presencia = None

try:
    while True:
        ahora = time.time()

        if estado == "esperando_presencia":
            if sensor.detectar_movimiento():
                INTERVALO = RAPIDO
                contPresencia += 1
                print(f"Detección positiva: #{contPresencia}")
                if contPresencia >= CHEQUEOS_REQUERIDOS:
                    print("Person detected -> Send comand preset.")
                    ser.write('{"ps":10}\r'.encode())
                    print("-- Iluminación activada --")
                    estado = "presencia_confirmada"
                    tiempo_confirmacion_presencia = ahora
                    contPresencia = 0
                    INTERVALO = LENTO  # resetear intervalo
            else:
                if contPresencia > 0:
                    print("Reset contador.")
                contPresencia = 0
            time.sleep(INTERVALO)

        elif estado == "presencia_confirmada":
            if ahora - tiempo_confirmacion_presencia >= TIEMPO_ESPERA_AUSENCIA:
                estado = "esperando_ausencia"
                print("-- Comenzando detección de ausencia --")
            time.sleep(INTERVALO)

        elif estado == "esperando_ausencia":
            if not sensor.detectar_movimiento():
                INTERVALO = RAPIDO
                contAusencia += 1
                print(f"[BUSCANDO AUSENCIA] Detección negativa #{contAusencia}")
                if contAusencia >= CHEQUEOS_REQUERIDOS:
                    print("[CONFIRMADO] Persona se fue.")
                    # Si querés apagar luces, hacelo acá:
                    ser.write('{"ps":19}\r'.encode())  # X = preset de apagado
                    estado = "esperando_presencia"
                    contAusencia = 0
                    INTERVALO = LENTO  # resetear intervalo
            else:
                if contAusencia > 0:
                    print("Reset contador.")
                contAusencia = 0
            time.sleep(INTERVALO)

        

except KeyboardInterrupt:
    print("\nPrograma finalizado por el usuario.")


