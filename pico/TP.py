from __future__ import print_function
import sys
import os
import time
import json
import requests
from DFRobot_C4001 import *
# --------- CONFIGURACIÓN - PICO---------
import serial
import struct
import wave
from datetime import datetime
import pvporcupine
import pvrhino
from pvrecorder import PvRecorder

MODO_PORCUPINE=0
MODO_RHINO=1

#-------- PORCUPINE --------
keyword_paths = ['holaalma.ppn']
library_path=None
model_path = "porcupine_params_es.pv"
sensitivities = ""

#--------- RHINO --------
rhino_library_path=None
rhino_model_path="rhino_params_es.pv"
rhino_context_path="alma_1_es.rhn"
rhino_sensitivity=0.5
rhino_endpoint_duration_sec=0.5
rhino_require_endpoint=True

#COMUN
access_key = "O7D9uT2joAvNPwbyExhfvMMGy9ki6AtTi2YhgJn9bGaCqoo9+sXNeA=="
#audio_device_index=9           #USAR 9 cuando se ejecuta con SUDO
audio_device_index=1
output_path=None

modo=MODO_PORCUPINE
wakeupTime=None

ser=serial.Serial(port='/dev/ttyAMA0', baudrate=115200)
#ser.setRTS(False)
#ser.setDTR(False)
time.sleep(2)

def pico_init():

    global modo
    global porcupine, rhino, recorder, wav_file
    global keywords, keyword_paths
    # LISTA LOS DISPOSITIVOS DE AUDIO DISPONIBLES 
    for i, device in enumerate(PvRecorder.get_available_devices()):
        print('Device %d: %s' % (i, device))
    sensitivities = [0.5] * len(keyword_paths)
    #PORCUPINE INIT
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            library_path=library_path,
            model_path=model_path,
            keyword_paths=keyword_paths,
            sensitivities=sensitivities)
    except pvporcupine.PorcupineInvalidArgumentError as e:
        print("One or more arguments provided to Porcupine is invalid: ")
        print(e)
        raise e
    except pvporcupine.PorcupineActivationError as e:
        print("AccessKey activation error")
        raise e
    except pvporcupine.PorcupineActivationLimitError as e:
        print("AccessKey '%s' has reached it's temporary device limit" % access_key)
        raise e
    except pvporcupine.PorcupineActivationRefusedError as e:
        print("AccessKey '%s' refused" % access_key)
        raise e
    except pvporcupine.PorcupineActivationThrottledError as e:
        print("AccessKey '%s' has been throttled" % access_key)
        raise e
    except pvporcupine.PorcupineError as e:
        print("Failed to initialize Porcupine")
        raise e

    keywords = list()
    for x in keyword_paths:
        keyword_phrase_part = os.path.basename(x).replace('.ppn', '').split('_')
        if len(keyword_phrase_part) > 6:
            keywords.append(' '.join(keyword_phrase_part[0:-6]))
        else:
            keywords.append(keyword_phrase_part[0])
    print('Porcupine version: %s' % porcupine.version)
    #RHINO INIT
    try:
        rhino = pvrhino.create(
            access_key=access_key,
            library_path=rhino_library_path,
            model_path=rhino_model_path,
            context_path=rhino_context_path,
            sensitivity=rhino_sensitivity,
            endpoint_duration_sec=rhino_endpoint_duration_sec,
            require_endpoint=rhino_require_endpoint)
    except pvrhino.RhinoInvalidArgumentError as e:
        print("One or more arguments provided to Rhino is invalid: ", args)
        print(e)
        raise e
    except pvrhino.RhinoActivationError as e:
        print("AccessKey activation error")
        raise e
    except pvrhino.RhinoActivationLimitError as e:
        print("AccessKey '%s' has reached it's temporary device limit" % args.access_key)
        raise e
    except pvrhino.RhinoActivationRefusedError as e:
        print("AccessKey '%s' refused" % args.access_key)
        raise e
    except pvrhino.RhinoActivationThrottledError as e:
        print("AccessKey '%s' has been throttled" % args.access_key)
        raise e
    except pvrhino.RhinoError as e:
        print("Failed to initialize Rhino")
        raise e

    print('Rhino version: %s' % rhino.version)
    print('Context info: %s' % rhino.context_info)

    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=audio_device_index)
    
    recorder.start()

    print ("PORCUPINE FRAME_LEN:" + str(porcupine.frame_length))
    print ("RHINO FRAME_LEN:" + str (rhino.frame_length))

    wav_file = None
    if output_path is not None:
        wav_file = wave.open(output_path, "w")
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)

    print('Listening ... (press Ctrl+C to exit)')
    
def pico_run():
    global modo
    pcm = recorder.read()
    if modo==MODO_PORCUPINE:
        result = porcupine.process(pcm)
        if result >= 0:
            print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
            ser.write ('{"ps":8}\r'.encode())
            modo=MODO_RHINO

    elif modo==MODO_RHINO:
        is_finalized = rhino.process(pcm)
        if is_finalized:
            inference = rhino.get_inference()
            if inference.is_understood:
                print('{')
                print("  intent : '%s'" % inference.intent)
                print('  slots : {')
                for slot, value in inference.slots.items():
                    print("    %s : '%s'" % (slot, value))
                print('  }')
                print('}\n')
                ser.write ('{"ps":1}\r'.encode())
                if inference.slots["estado"]=="feliz":
                    ser.write ('{"ps":5}\r'.encode())
                    print ("FELIZ!")
                    
                if inference.slots["estado"]=="enojado":

                    ser.write ('{"ps":4}\r'.encode())
                    print ("ENOJADO!")
                if inference.slots["estado"]=="triste":

                    ser.write ('{"ps":3}\r'.encode())
                    print ("TRISTE!")
                if inference.slots["estado"] == "sorprendido":

                    ser.write('{"ps":11}\r'.encode())
                    print("SORPRESA!")
                if inference.slots["estado"] == "miedo":

                    ser.write('{"ps":10}\r'.encode())
                    print("MIEDO!")                        
                if inference.slots["estado"] == "confundido":

                    ser.write('{"ps":16}\r'.encode())
                    print("CONFUNDIDO!")
                if inference.slots["estado"] == "esperanzado":

                    ser.write('{"ps":14}\r'.encode())
                    print("ESPERANZADO!")
                if inference.slots["estado"] == "tranquilo":

                    ser.write('{"ps":13}\r'.encode())
                    print("TRANQUILO!")
                if inference.slots["estado"] == "avergonzado":

                    ser.write('{"ps":17}\r'.encode())
                    print("AVERGONZADO!")

                ser.write ('{"ps":6}\r'.encode())
                #else:
                #    ser.write ('{"ps":1}\r'.encode())

                modo=MODO_PORCUPINE
            else:
                print("Didn't understand the command.\n")
            #if wav_file is not None:
            #    wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))
            
#ENVIA EL EFECO DE INICIO DE LOS LEDS
# ---------------------------------------

ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
ser.write ('{"ps":2}\r'.encode())

# --------- CONFIGURACIÓN ---------
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
    pico_init()
    setup_sensor()
    radarTrue = True        # Para controlar el estado de detección
    clima_interval = 60     # segundos
    deteccion_interval = 1  # segundos

    ultima_actualizacion_clima = 0
    ultimo_chequeo_presencia = 0
    datos_clima = None

    print("\nIniciando monitoreo. Ctrl+C para salir.\n")
    
    try:
        while True:
            ahora = time.time()
            pico_run()

            # Obtener clima cada minuto
            if ahora - ultima_actualizacion_clima >= clima_interval:
                datos_clima = obtener_openweathermap(CIUDAD)
                if datos_clima:
                    vel = datos_clima['viento_velocidad']
                    dir = datos_clima['viento_direccion']
                    ix = map_range(vel, 0, 20, 0, 255)
                    sx = map_range(dir, 0, 360, 0, 255)
                else:
                    print("[CLIMA] No se pudo obtener datos del clima.")
                    # Valores por defecto
                    vel, dir, ix, sx = 125, 125, 0, 0 
                # Enviar comando a WLED    
                comando = {"seg": [{"ix": ix, "sx": sx}]}
                json_cmd = json.dumps(comando)
                ser.write((json_cmd + '\r').encode())
                
                print(f"[CLIMA] Vel: {vel:.2f} m/s (ix: {ix}) | Dir: {dir}° (sx: {sx})")
                
                # Actualizar tiempo de la última actualización del clima
                ultima_actualizacion_clima = ahora

            # Chequear detección cada 1 segundo
            if ahora - ultimo_chequeo_presencia >= deteccion_interval:
                if radar.motion_detection() == 1:
                    print("[DETECCIÓN] Movimiento detectado -> Enviando comando preset.")
                    if radarTrue:
                        ser.write('{"ps":10}\r'.encode())
                        print("-- Iluminacion activada --")
                        radarTrue = False
                else:
                    radarTrue = True
                    print(" Sin presencia ")
                ultimo_chequeo_presencia = ahora

            time.sleep(0.1)  # evitar uso excesivo de CPU

    except KeyboardInterrupt:
        print("\n Programa finalizado por el usuario.")
    finally:
        ser.close()
        recorder.delete()
        porcupine.delete()
        if wav_file is not None:
            wav_file.close()

if __name__ == "__main__":
    main()
