
import RPi.GPIO as GPIO
import time
import mqtt_publish

import constants

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


_int_adr = {}

for _input in constants.GPIO_IN:
    if _input == constants.name:
        _id = constants.GPIO_IN[_input][1]
        _hks = constants.GPIO_IN[_input][0]
        GPIO.setup(_id, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        _int_adr[_id] = _hks

def main():
    tuer = gpio_input_monitoring()
    tuer.monitor()

class gpio_input_monitoring:

    def __init__(self):
        self.data = []
        self.alt = {}
        for _input in _int_adr:
            wert = GPIO.input(_input)
            self.alt[_input] = wert

    def monitor(self):
        while True:
            counter = 0
            for _input in _int_adr:
                wert = GPIO.input(_input)
                pre_wert = self.alt[_input]
                dicti = {'Value':wert, 'Name': 'GPIO.' + constants.name + '.' + str(_input)}
                if wert <> pre_wert:
#                    server.sendto(str(dicti),(constants.server1,constants.broadPort))
                    mqtt_publish.mqtt_pub('Inputs/Satellite/' + constants.name + '/' + str(_input),dicti)
                    self.alt[_input] = wert
                if counter >= 1800:
#                    server.sendto(str(dicti),(constants.server1,constants.broadPort))
                    mqtt_publish.mqtt_pub('Inputs/Satellite/' + constants.name + '/' + str(_input),dicti)                    
            counter += 1
            time.sleep(0.1)
            if counter >= 1800:
                counter = 0

if  __name__ =='__main__':main()
