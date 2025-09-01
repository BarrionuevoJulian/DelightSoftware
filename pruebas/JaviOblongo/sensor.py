import time
from DFRobot_C4001 import *

class PresenciaSensor:
    def __init__(self, modo='I2C'):
        self.modo = modo
        if modo == 'I2C':
            self.radar = DFRobot_C4001_I2C(0x01, 0x2A)
        else:
            self.radar = DFRobot_C4001_UART(9600)

    def configurar(self):
        print("Inicializando sensor...")
        while not self.radar.begin():
            print("Sensor initialize failed!!")
            time.sleep(1)

        self.radar.set_sensor_mode(EXIST_MODE)
        self.radar.set_detect_thres(11, 100, 11)
        self.radar.set_detection_range(30, 240, 240)
        self.radar.set_trig_sensitivity(1)
        self.radar.set_keep_sensitivity(1)
        self.radar.set_delay(50, 4)
        self.radar.set_pwm(50, 0, 10)
        self.radar.set_io_polaity(1)
        print("Sensor listo.")

    def detectar_movimiento(self):
        return self.radar.motion_detection() == 1