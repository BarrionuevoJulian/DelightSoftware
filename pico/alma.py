import os
import struct
import wave
from datetime import datetime

import pvporcupine
import pvrhino
from pvrecorder import PvRecorder
import serial
import time

MODO_PORCUPINE = 0
MODO_RHINO = 1

# PORCUPINE
keyword_paths = ['holaalma.ppn']
library_path = None
model_path = "porcupine_params_es.pv"
sensitivities = ""

# RHINO
rhino_library_path = None
rhino_model_path = "rhino_params_es.pv"
rhino_context_path = "alma_1_es.rhn"
rhino_sensitivity = 0.5
rhino_endpoint_duration_sec = 0.5
rhino_require_endpoint = True

# COMUN
access_key = "O7D9uT2joAvNPwbyExhfvMMGy9ki6AtTi2YhgJn9bGaCqoo9+sXNeA=="
# audio_device_index=9           # USAR 9 cuando se ejecuta con SUDO
audio_device_index = 1
output_path = None

modo = MODO_PORCUPINE
wakeupTime = None

ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200)
#time.sleep(1)

# ENVIA EL EFECTO DE INICIO DE LOS LEDS
ser.write('{"ps":5}\r'.encode())

def main():
    global modo

    # LISTA LOS DISPOSITIVOS DE AUDIO DISPONIBLES
    for i, device in enumerate(PvRecorder.get_available_devices()):
        print('Device %d: %s' % (i, device))

    sensitivities = [0.5] * len(keyword_paths)

    # PORCUPINE INIT
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
        print("AccessKey '%s' has reached its temporary device limit" % access_key)
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

    keywords = []
    for x in keyword_paths:
        keyword_phrase_part = os.path.basename(x).replace('.ppn', '').split('_')
        if len(keyword_phrase_part) > 6:
            keywords.append(' '.join(keyword_phrase_part[0:-6]))
        else:
            keywords.append(keyword_phrase_part[0])

    print('Porcupine version: %s' % porcupine.version)

    # RHINO INIT
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
        print("AccessKey '%s' has reached its temporary device limit" % access_key)
        raise e
    except pvrhino.RhinoActivationRefusedError as e:
        print("AccessKey '%s' refused" % access_key)
        raise e
    except pvrhino.RhinoActivationThrottledError as e:
        print("AccessKey '%s' has been throttled" % access_key)
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

    print("PORCUPINE FRAME_LEN:", porcupine.frame_length)
    print("RHINO FRAME_LEN:", rhino.frame_length)

    wav_file = None
    if output_path is not None:
        wav_file = wave.open(output_path, "w")
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)

    print('Listening ... (press Ctrl+C to exit)')

    try:
        while True:
            pcm = recorder.read()
            if modo == MODO_PORCUPINE:
                result = porcupine.process(pcm)
                if result >= 0:
                    print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
                    ser.write('{"ps":8}\r'.encode())
                    modo = MODO_RHINO

            elif modo == MODO_RHINO:
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
                        #ser.write('{"ps":1}\r'.encode())
                        #ser.flush()
                        if inference.slots["estado"] == "feliz":
                            #time.sleep(7)
                            ser.write('{"ps":18}\r'.encode())
                            #ser.flush()
                            print("FELIZ!")
                        elif inference.slots["estado"] == "enojado":
                            ser.write('{"ps":4}\r'.encode())
                            print("ENOJADO!")
                        elif inference.slots["estado"] == "triste":
                            ser.write('{"ps":3}\r'.encode())
                            print("TRISTE!")
                        elif inference.slots["estado"] == "miedo":
                            ser.write('{"ps":10}\r'.encode())
                            print("MIEDO!")
                        elif inference.slots["estado"] == "esperanzado":
                            ser.write('{"ps":14}\r'.encode())
                            print("ESPERANZADO!")
                        elif inference.slots["estado"] == "tranquilo":
                            ser.write('{"ps":11}\r'.encode())
                            print("TRANQUILO!")
                        elif inference.slots["estado"] == "avergonzado":
                            ser.write('{"ps":17}\r'.encode())
                            print("AVERGONZADO!")
                        #ser.write('{"ps":6}\r'.encode())
                        modo = MODO_PORCUPINE
                    else:
                        print("Didn't understand the command.\n")

    except KeyboardInterrupt:
        print('Stopping ...')

    finally:
        recorder.delete()
        porcupine.delete()
        if wav_file is not None:
            wav_file.close()

if __name__ == '__main__':
    main()
