import os
import struct
import wave
from datetime import datetime
import pvporcupine
import pvrhino
from pvrecorder import PvRecorder
import serial

MODO_PORCUPINE = 0
MODO_RHINO = 1

class VoiceProcessor:
    def __init__(self, access_key, audio_device_index):
        self.access_key = access_key
        self.audio_device_index = audio_device_index
        self.modo = MODO_PORCUPINE
        self.porcupine = None
        self.rhino = None
        self.recorder = None
        self.wav_file = None
        self.ser = None
        self.keywords = []
        self.keyword_paths = ['holaalma.ppn']
        self.model_path = "porcupine_params_es.pv"
        self.rhino_model_path = "rhino_params_es.pv"
        self.rhino_context_path = "alma_1_es.rhn"

    def iniciar_serial(self, port='/dev/serial0'):
        self.ser = serial.Serial(port, baudrate=115200, timeout=1)
        self.ser.write('{"ps":2}\r'.encode())

    def iniciar_porcu_rhino(self):
        sensitivities = [0.5] * len(self.keyword_paths)
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            model_path=self.model_path,
            keyword_paths=self.keyword_paths,
            sensitivities=sensitivities
        )
        self.keywords = [os.path.basename(k).replace('.ppn', '') for k in self.keyword_paths]

        self.rhino = pvrhino.create(
            access_key=self.access_key,
            model_path=self.rhino_model_path,
            context_path=self.rhino_context_path,
            sensitivity=0.5,
            endpoint_duration_sec=0.5,
            require_endpoint=True
        )

        self.recorder = PvRecorder(
            frame_length=self.porcupine.frame_length,
            device_index=self.audio_device_index
        )
        self.recorder.start()

    def correr(self):
        pcm = self.recorder.read()

        if self.modo == MODO_PORCUPINE:
            result = self.porcupine.process(pcm)
            if result >= 0:
                print(f"[{datetime.now()}] Detected {self.keywords[result]}")
                self.ser.write('{"ps":8}\r'.encode())
                self.modo = MODO_RHINO

        elif self.modo == MODO_RHINO:
            if self.rhino.process(pcm):
                inference = self.rhino.get_inference()
                if inference.is_understood:
                    estado = inference.slots.get("estado", "")
                    print(f"Intent: {inference.intent}, Estado: {estado}")

                    preset_map = {
                        "feliz": 5,
                        "enojado": 4,
                        "triste": 3,
                        "sorprendido": 11,
                        "miedo": 10,
                        "confundido": 16,
                        "esperanzado": 14,
                        "tranquilo": 13,
                        "avergonzado": 17,
                    }
                    self.ser.write('{"ps":1}\r'.encode())
                    if estado in preset_map:
                        self.ser.write(f'{{"ps":{preset_map[estado]}}}\r'.encode())
                    self.ser.write('{"ps":6}\r'.encode())
                else:
                    print("[!] No se entendió el comando.")
                self.modo = MODO_PORCUPINE

    def cerrar(self):
        if self.recorder:
            self.recorder.delete()
        if self.porcupine:
            self.porcupine.delete()
        if self.wav_file:
            self.wav_file.close()
        if self.ser:
            self.ser.close()
