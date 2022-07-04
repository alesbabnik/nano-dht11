import network                # For operation of WiFi network
import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Needed to run any MicroPython code
import machine                # Interfaces with hardware components
from machine import Pin
import dht
import cred                   # Wifi credentials

def main():
    # BEGIN SETTINGS

    # Adafruit IO (AIO) configuration
    AIO_SERVER = "io.adafruit.com"
    AIO_PORT = 1883
    AIO_USER = "{username}"
    AIO_KEY = "aio_XXXXXXX"
    AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
    AIO_TEMP_FEED = "{username}/feeds/{feedname}"
    AIO_HUM_FEED = "{username}/feeds/{feedname}"

    # Other
    DELAY = 15

    # Pins
    DHT11 = dht.DHT11(Pin(26))
    LED_ON=Pin(27,Pin.OUT)
    LED_ERR=Pin(28,Pin.OUT)

    # END SETTINGS


    # WIFI
    sta_if = network.WLAN(network.STA_IF)       # Put modem on Station mode
    if not sta_if.isconnected():                # Check if already connected
        print('Connecting to network...')
        sta_if.active(True)                     # Activate network interface
        sta_if.connect(cred.WIFI_SSID, cred.WIFI_PASS)     # Your WiFi Credential
        # Check if it is connected otherwise wait
        while not sta_if.isconnected():
            pass
    # Print the IP assigned by router
    print('Network config:', sta_if.ifconfig())

    def led_error():
        LED_ON.value(0)                 #Turn off the green LED
        while 1:                        #Start blinking the red LED
            LED_ERR.value(1)
            time.sleep(0.5)
            LED_ERR.value(0)
            time.sleep(0.5)

    def send_data(feed, value):
        print("Publishing: {0} to {1} ... ".format(value, feed), end='')
        try:
            client.publish(topic=feed, msg=str(value))
            print("DONE")
            LED_ERR.value(0)
        except Exception as e:
            print("FAILED")
            LED_ERR.value(1)


    # Use the MQTT protocol to connect to Adafruit IO
    client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)

    # Connect client to Adafruit IO servers
    client.connect()

    try:
        LED_ON.value(1)
        while 1:
            DHT11.measure()
            t = DHT11.temperature()
            h = DHT11.humidity()
            send_data(AIO_TEMP_FEED, t - 2)
            send_data(AIO_HUM_FEED, h)
            time.sleep(DELAY)
    except:
        # Turn on error LED and disconnect from Adafruit and Wifi
        led_error()
        client.disconnect()
        client = None
        sta_if.disconnect()
        sta_if = None
        print("Disconnected from Adafruit IO.")


if __name__ == '__main__':
    main()
