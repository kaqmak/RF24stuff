#!/usr/bin/env python

#
# Example using Dynamic Payloads
# 
#  This is an example of how to use payloads of a varying (dynamic) size.
# 

from __future__ import print_function
import time
from RF24 import *
import RPi.GPIO as GPIO
import struct
import re
irq_gpio_pin = None

########### USER CONFIGURATION ###########
# See https://github.com/TMRh20/RF24/blob/master/RPi/pyRF24/readme.md

# CE Pin, CSN Pin, SPI Speed

# Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 8Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

#RPi B
# Setup for GPIO 15 CE and CE1 CSN with SPI Speed @ 8Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

#RPi B+
# Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
#radio = RF24(RPI_BPLUS_GPIO_J8_15, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

#radio = RF24(RPI_V2_GPIO_P1_15, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ);

# RPi Alternate, with SPIDEV - Note: Edit RF24/arch/BBB/spi.cpp and  set 'this->device = "/dev/spidev0.0";;' or as listed in /dev
radio = RF24(22, 0);


# Setup for connected IRQ pin, GPIO 24 on RPi B+; uncomment to activate
#irq_gpio_pin = RPI_BPLUS_GPIO_J8_18
#irq_gpio_pin = 24

##########################################
def try_read_data(channel=0):
    if radio.available():
        while radio.available():
            len = radio.getDynamicPayloadSize()
            receive_payload = radio.read(len)
            #print('Got payload size={} value="{}"'.format(len, receive_payload.decode('utf-8')))
            #print('Got payload size={} value="{}"'.format(len, receive_payload))
            
            tempStr, humStr = receive_payload.decode('utf-8').split('X')
            print(re.findall(r'\d+\.*\d*', tempStr)[0])
            temp = float(re.findall(r'\d+\.*\d*', tempStr)[0] )
            hum = float(re.findall(r'\d+\.*\d*', humStr)[0] )
            print('Recieved Temperature:{} C, Humidity:{} %'.format(temp,hum))
            #print(struct.unpack("PPPP", ''.join(chr(c) for c in receive_payload)))
            #hmm="".join(map(chr, receive_payload))
            #print(hmm)
            #print(''.join(chr(c) for c in receive_payload) )
            # First, stop listening so we can talk
            radio.stopListening()

            # Send the final one back.
            radio.write(receive_payload)
            print('Sent response.')

            # Now, resume listening so we catch the next packets.
            radio.startListening()

pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
min_payload_size = 4
max_payload_size = 32
payload_size_increments_by = 1
next_payload_size = min_payload_size
inp_role = 'none'
send_payload = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ789012'
millis = lambda: int(round(time.time() * 1000))

print('pyRF24/examples/pingpair_dyn/')
radio.begin()
radio.enableDynamicPayloads()
radio.setRetries(5,15)
radio.printDetails()



print('Role: Pong Back, awaiting transmission')
if irq_gpio_pin is not None:
    # set up callback for irq pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(irq_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(irq_gpio_pin, GPIO.FALLING, callback=try_read_data)

radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1,pipes[0])
radio.startListening()

# forever loop
while 1:
        # Pong back role.  Receive each packet, dump it out, and send it back

        # if there is data ready
        if irq_gpio_pin is None:
            # no irq pin is set up -> poll it
            try_read_data()
        else:
            # callback routine set for irq pin takes care for reading -
            # do nothing, just sleeps in order not to burn cpu by looping
            time.sleep(1000)

