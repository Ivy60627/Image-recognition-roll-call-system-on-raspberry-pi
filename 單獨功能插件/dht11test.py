import time
import adafruit_dht
from board import *

GPIO_PIN= D4

dht_device = adafruit_dht.DHT11(GPIO_PIN, use_pulseio = False)
try:
    while True:
        try:
            t=dht_device.temperature
            h=dht_device.humidity
        except RuntimeError:
            print('failed')
        if h is not None and t is not None:
            print('溫度={0:0.1f}度 濕度={1:0.1f}%'.format(t, h))
                
        else:
            print('溫度= -1 度 濕度= -1 %')
        time.sleep(5)
except KeyboardInterrupt:
    print('exit')