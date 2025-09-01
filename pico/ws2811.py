import time
from threading import Thread
from rpi_ws281x import PixelStrip, Color


# LED strip configuration:
LED_COUNT = 16        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

strip=None

color=Color(0,0,0)
EFECTO_STANDBY=0
EFECTO_WAKEUP=1
EFECTO_FELIZ=2
EFECTO_MUY_FELIZ=3
EFECTO_TRISTE=4
EFECTO_ENOJADO=5
EFECTO_MUY_ENOJADO=6
EFECTO_OTRO=10
EFECTO_NONE=-1
EFECTO_SALIR=-10
efecto=EFECTO_STANDBY

th=None

def latidoAzul(strip, min_val=0, max_val=255, wait_ms=10):
    global color
    brillo = 0
    for brillo in range(min_val, max_val):
        for i in range(strip.numPixels()):
            color=Color(0, 0,brillo)
            strip.setPixelColor(i, color)
            strip.show()
        if (efecto!=EFECTO_STANDBY):
            return
        time.sleep(wait_ms / 1000.0)
    
    for brillo in range(max_val, min_val, -1):
        for i in range(strip.numPixels()):
            color=Color(0, 0,brillo)
            strip.setPixelColor(i, color)
            strip.show()
        if (efecto!=EFECTO_STANDBY):
            return
        time.sleep(wait_ms / 1000.0)
def efectoFeliz(strip, max_val=255, wait_ms=1):
     global color
     global efecto
     min_val=0
     for brillo in range(min_val, max_val, 2):
        for i in range(strip.numPixels()):
            color=Color(0, brillo, 0)
            strip.setPixelColor(i, color)
            strip.show()
        if (efecto!=EFECTO_FELIZ):
            return
        time.sleep(wait_ms / 1000.0)

     efecto=EFECTO_NONE

def efectoEnojado(strip, max_val=255, wait_ms=1):
     global color
     global efecto
     min_val=0
     for brillo in range(min_val, max_val, 2):
        for i in range(strip.numPixels()):
            color=Color(brillo, 0, 0)
            strip.setPixelColor(i, color)
            strip.show()
        if (efecto!=EFECTO_ENOJADO):
            return
        time.sleep(wait_ms / 1000.0)

     efecto=EFECTO_NONE

def efectoWakeup(strip):
    global color
    global efecto
    max_val=color.b
    min_val=0
    for brillo in range(max_val, min_val, -4):
        for i in range(strip.numPixels()):
            color=Color(0, 0,brillo)
            strip.setPixelColor(i, color)
            strip.show()
        if (efecto!=EFECTO_WAKEUP):
            return
        time.sleep(0.001)
    
    
    max_val=100
    min_val=0
    for brillo in range(min_val, max_val, 3):
        for i in range(strip.numPixels()):
            color=Color(brillo, brillo,brillo)
            strip.setPixelColor(i, color)
            strip.show()
        if (efecto!=EFECTO_WAKEUP):
            return
        time.sleep(0.001)

    max_val=100
    min_val=30
    for brillo in range(max_val, min_val, -3):
        for i in range(strip.numPixels()):
            color=Color(brillo, brillo,brillo)
            strip.setPixelColor(i, color)
            strip.show()
        if (efecto!=EFECTO_WAKEUP):
            return
        time.sleep(0.001)




    efecto=EFECTO_NONE

    return

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def efectoLoop():
    global color
    global efecto

    print ("efectoLoop START!")
    while True:
        if efecto==EFECTO_STANDBY:
            latidoAzul(strip)
        elif efecto==EFECTO_WAKEUP:
            efectoWakeup(strip)
        elif efecto==EFECTO_FELIZ:
            efectoFeliz(strip)
        elif efecto==EFECTO_ENOJADO:
            efectoEnojado(strip)
        elif efecto==EFECTO_SALIR:
            break
    print ("efectoLoop END!")

    

def startThread():
    global th
    th=Thread(target=efectoLoop)
    th.start()

def stopThread():
    global th
    efecto=EFECTO_SALIR
    th.join()

def init():
    global strip
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    startThread()

# Main program logic follows:
#if __name__ == '__main__':
    # Process arguments

    # Create NeoPixel object with appropriate configuration.
    
    # Intialize the library (must be called once before other functions).
    #init();

    #print ("A")
    #time.sleep(10)
    #print ("B")
    #efecto=EFECTO_WAKEUP
    #time.sleep(15)
    #efecto=EFECTO_SALIR
    #th.join()
    #print ("C")
    #print ("EXIT")
