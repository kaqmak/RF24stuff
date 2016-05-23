#!/usr/bin/env python

#
# Example using Dynamic Payloads
#
#  This is an example of how to use payloads of a varying (dynamic) size.


import time
import datetime
from RF24 import *
import logging
import re  # regular expressions
import plotly
import plotly.plotly as py  # (*) To communicate with Plotly's server, sign in with credentials file
import plotly.tools as tls  # (*) Useful Python/Plotly tools
import plotly.graph_objs as go  # (*) Graph objects to piece together plots
import numpy as np  # (*) numpy for math functions and arrays

############################ plotly intialization################
plotlyTitle = 'Hmmmm'

#stream_ids = tls.get_credentials_file()['stream_ids']

# Get stream id from stream id list
#stream_id = stream_ids[0]

# Make instance of   stream id object
# stream = Stream(
#     token=stream_id,  # (!) link stream id to 'token' key
#     maxpoints=500      # (!) keep a max of 80 pts on screen
# )

# Initialize trace of streaming plot by embedding the unique stream_id
trace1 = go.Scatter(
    x=[],
    y=[],
    mode='lines+markers',
    #ine=Line(opacity=0.8),  # reduce opacity
    #marker=Marker(size=12),  # increase marker size
    #stream=stream         # (!) embed stream id, 1 per trace
)

data = go.Data([trace1])

# Add title to layout object
layout = go.Layout(title=plotlyTitle)

# Make a figure object
fig = go.Figure(data=data, layout=layout)

# (@) Send fig to Plotly, initialize streaming plot, open new tab
#unique_url = py.plot(fig, filename='tis',fileopt='extend')

# (@) Make instance of the Stream link object, 
#     with same stream id as Stream id object
#s = py.Stream(stream_id)

# (@) Open the stream
#s.open()
# Delay start of stream by 5 sec (time to switch tabs)
#time.sleep(5)
#####################################################


############ loggin config ###############
#logging.basicConfig(filename='example.log', level=logging.DEBUG, format='%(asctime)s\t%(message)s') #  logs are appended
# create logger with 'spam_application'
logger = logging.getLogger('__name__')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('example.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(asctime)s\t%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

########### USER CONFIGURATION ###########
# See https://github.com/TMRh20/RF24/blob/master/RPi/pyRF24/readme.md

# CE Pin, CSN Pin, SPI Speed

# Setup for GPIO 22 CE and GPIO 25 CSN with SPI Speed @ 1Mhz
#radio = RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_18, BCM2835_SPI_SPEED_1MHZ)

# Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 4Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_4MHZ)

#RPi B
# Setup for GPIO 15 CE and CE1 CSN with SPI Speed @ 8Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

#RPi B+
# Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
radio = RF24(RPI_BPLUS_GPIO_J8_22, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

##########################################

pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
min_payload_size = 4
max_payload_size = 32
payload_size_increments_by = 1
next_payload_size = min_payload_size
inp_role = 'none'
send_payload = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ789012'
millis = lambda: int(round(time.time() * 1000))
logPeriod = 1

#print 'pyRF24/examples/pingpair_dyn/'
radio.begin()
radio.enableDynamicPayloads()
radio.setRetries(5, 15)
radio.printDetails()


print('Role: Pong Back, awaiting transmission')
radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1, pipes[0])
radio.startListening()

# forever loop
while 1:
        # Pong back role.  Receive each packet, dump it out, and send it back
        # if there is data ready
    if radio.available():
        while radio.available():
            # Fetch the payload, and see if this was the last one.
            len = radio.getDynamicPayloadSize()
            receive_payload = radio.read(len)

            # Spew it
            print 'Got payload size=', len, ' value="' + receive_payload + '"'
            print type(receive_payload)
            logger.info(receive_payload)  # store in a file

            #send to plotly
            x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            #y = float(re.findall(r'\d+\.*\d*', receive_payload))  # find number followed by 0 or more . followed by zero or more ints
            y = receive_payload
            # (-) Both x and y are numbers (i.e. not lists nor arrays)
            # (-) Both x and y are numbers (i.e. not lists nor arrays)
            # (@) write to Plotly stream!
            #s.write(dict(x=x, y=y))

            #new_data = go.Scatter(x=x, y=y)
            #data = go.Data([new_data])
            #unique_url = py.plot(data, filename='tis', fileopt='extend')

        # First, stop listening so we can talk
        radio.stopListening()

        # Send the final one back.
        radio.write(receive_payload)
        print 'Sent response.'

        # Now, resume listening so we catch the next packets.
        radio.startListening()

        time.sleep(logPeriod)
