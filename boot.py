import network
import micropython
import time 
from secrets import secrets
import machine
from machine import Pin
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Conversions between binary data and various encodings

led = Pin("LED", Pin.OUT)
led.toggle()
time.sleep(2)

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "userName adafruit"
AIO_KEY = "io key in adafruit"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_MAGNET_FEED = "userName/feeds/magnet"

def do_connect():
    wlan = network.WLAN(network.STA_IF)         # Put modem on Station mode

    if not wlan.isconnected():                  # Check if already connected
        print('connecting to network...')
        wlan.active(True)                       # Activate network interface
        # set power mode to get WiFi power-saving off (if needed)
        wlan.config(pm = 0xa11140)
        wlan.connect(secrets["ssid"], secrets["password"])  # Your WiFi Credential
        print('Waiting for connection...', end='')
        # Check if it is connected otherwise wait
        while not wlan.isconnected() and wlan.status() >= 0:
            print('.', end='')
            time.sleep(1)
    # Print the IP assigned by router
    ip = wlan.ifconfig()[0]
    print('\nConnected on {}'.format(ip))
    return ip 

# WiFi Connection
try:
    ip = do_connect()
    led.toggle()
    time.sleep(10)
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)

# Subscribed messages will be delivered to this callback
try: 
    client.connect()
    print("Connected to %s, subscribed to %s topic" % (AIO_SERVER, AIO_MAGNET_FEED))
except Exception as e:
    print("Error:", e)
    led.toggle()
    time.sleep(3)
    machine.reset()

# Set the pin for reed switch
Reed_switch = Pin(27, Pin.IN)

while True:
    magnet = Reed_switch.value()
    if Reed_switch.value() == 0:
        print("Magnet detected...")
    else:
        print("No magnet detected...")
    
    print("Publishing: {0} to {1} ... ".format(magnet, AIO_MAGNET_FEED), end='')
    try:
        client.publish(topic=AIO_MAGNET_FEED, msg=str(magnet))
        print("DONE")
    except Exception as e:
        pass
    led.toggle()
    time.sleep(5) 

