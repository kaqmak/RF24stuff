/*
 Copyright (C) 2011 J. Coliz <maniacbug@ymail.com>

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 version 2 as published by the Free Software Foundation.
 */

/**
 * Example using Dynamic Payloads 
 *
 * This is an example of how to use payloads of a varying (dynamic) size. 
 */

#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "DHT.h"
#define TEMPINPIN 9     // DHT signal pin
#define TEMPPWRPIN 4//DHT power pin
#define DHTTYPE DHT22
DHT dht(TEMPINPIN, DHTTYPE);
//#include <printf.h>  // Printf is used for debug 

String perstr;
struct measurementSet
{
  float hum;
  float temp;
} 
dataParams;
//----------------RF24 Hardware configuration.---------------------------------

// Set up nRF24L01 radio on SPI bus plus pins 7 & 8
RF24 radio(7,8);

// sets the role of this unit in hardware.  Connect to GND to be the 'pong' receiver
// Leave open to be the 'ping' transmitter
const int role_pin = 5;

//
// Topology
//

// Radio pipe addresses for the 2 nodes to communicate.
const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };

//
// Role management
//
// Set up role.  This sketch uses the same software for all the nodes
// in this system.  Doing so greatly simplifies testing.  The hardware itself specifies
// which node it is.
//
// This is done through the role_pin
//

// The various roles supported by this sketch
typedef enum { role_ping_out = 1, role_pong_back } role_e;

// The debug-friendly names of those roles
const char* role_friendly_name[] = { "invalid", "Ping out", "Pong back"};

// The role of the current running sketch
role_e role;

//
// Payload
//

const int min_payload_size = 4;
const int max_payload_size = 32;
const int payload_size_increments_by = 1;
//int next_payload_size = min_payload_size;
const int next_payload_size = 10;
//const int next_payload_size = 4;

char receive_payload[max_payload_size+1]; // +1 to allow room for a terminating NULL char
//---------------------------------------------------------



// Take a sensor reading and store in EEPROM
void logSensorReading() {
  // Take a moisture reading
//  digitalWrite(POWERPIN, HIGH);//turn sensor on
  //delay(10);
  //dataParams.h = (byte) analogRead(0)>>2;//decrease resolution to 1 byte
  //dataParams.h = analogRead(LIGHTPIN);//light reading
  //digitalWrite(POWERPIN, LOW);//turn sensor off

  //Measure temp and humidity
  digitalWrite(TEMPPWRPIN, HIGH);
  delay(10);
  dht.begin();
  delay(1000);
  dataParams.hum = dht.readHumidity();
  dataParams.temp = dht.readTemperature();
  Serial.print("Humidity");
  Serial.println(dataParams.hum);
  Serial.print("temp");
  Serial.println(dataParams.temp);
  digitalWrite(TEMPPWRPIN, LOW);
}

void setup(void)
{

  pinMode(TEMPINPIN, INPUT);      // sets the digital pin  as input
  pinMode(TEMPPWRPIN, OUTPUT);
  //digitalWrite(POWERPIN, LOW);
  //
  // Role
  //

  // set up the role pin
  pinMode(role_pin, INPUT);
  digitalWrite(role_pin,HIGH);
  delay(20); // Just to get a solid reading on the role pin

  // read the address pin, establish our role
  if ( digitalRead(role_pin) )
    role = role_ping_out;
  else
    role = role_pong_back;

  //
  // Print preamble
  //

  Serial.begin(115200);
  //printf_begin(); //Printf is used for debug
  
  //Serial.println(F("RF24/examples/pingpair_dyn/"));
  //Serial.print(F("ROLE: "));
  Serial.println(role_friendly_name[role]);

  //
  // Setup and configure rf radio
  //

  radio.begin();

  // enable dynamic payloads
  radio.enableDynamicPayloads();

  // optionally, increase the delay between retries & # of retries
  radio.setRetries(5,15);

  //
  // Open pipes to other nodes for communication
  //

  // This simple sketch opens two pipes for these two nodes to communicate
  // back and forth.
  // Open 'our' pipe for writing
  // Open the 'other' pipe for reading, in position #1 (we can have up to 5 pipes open for reading)

  if ( role == role_ping_out )
  {
    radio.openWritingPipe(pipes[0]);
    radio.openReadingPipe(1,pipes[1]);
  }
  else
  {
    radio.openWritingPipe(pipes[1]);
    radio.openReadingPipe(1,pipes[0]);
  }

  //
  // Start listening
  //

  radio.startListening();

  //
  // Dump the configuration of the rf unit for debugging
  //

  radio.printDetails();
}

void loop(void)
{
  //
  // Ping out role.  Repeatedly send the current time
  //

  if (role == role_ping_out)
  {
    // The payload will always be the same, what will change is how much of it we send.
    //static char send_payload[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ789012";
    char buffer[next_payload_size];
    char buffer2[next_payload_size];
    logSensorReading();
    //String send_payload[next_payload_size] = dtostrf(dataParams.hum, 8,6,buffer);
    //char* send_payload = dtostrf(dataParams.temp, 4,1,buffer);
    dtostrf(dataParams.temp, 4,1,buffer);
    strcat(buffer, "X"); // add first string
    dtostrf(dataParams.hum, 4,1,buffer2);
    strcat(buffer, buffer2); // add first string
    char* send_payload = buffer;
    
    Serial.print("send_payload:");
    Serial.println(send_payload);
    // First, stop listening so we can talk.
    radio.stopListening();

    // Take the time, and send it.  This will block until complete
    Serial.print(F("Now sending length "));
   // Serial.println(next_payload_size);
    //radio.write( send_payload, next_payload_size );
    
    int hm = 2;
    void *zeze;
    zeze = &hm;
    radio.write( zeze, 4 );

    // Now, continue listening
    radio.startListening();

    // Wait here until we get a response, or timeout
    unsigned long started_waiting_at = millis();
    bool timeout = false;
    while ( ! radio.available() && ! timeout )
      if (millis() - started_waiting_at > 500 )
        timeout = true;

    // Describe the results
    if ( timeout )
    {
      Serial.println(F("Failed, response timed out."));
    }
    else
    {
      // Grab the response, compare, and send to debugging spew
      uint8_t len = radio.getDynamicPayloadSize();
      
      // If a corrupt dynamic payload is received, it will be flushed
      if(!len){
        return; 
      }
      
      radio.read( receive_payload, len );

      // Put a zero at the end for easy printing
      receive_payload[len] = 0;

      // Spew it
      Serial.print(F("Got response size="));
      Serial.print(len);
      Serial.print(F(" value="));
      Serial.println(receive_payload);
      Serial.println("slut");
    }
    
    // Update size for next time.
    //next_payload_size += payload_size_increments_by;
    //if ( next_payload_size > max_payload_size )
    //  next_payload_size = min_payload_size;

    // Try again 1s later
    delay(100);
  }

  //
  // Pong back role.  Receive each packet, dump it out, and send it back
  //

}
// vim:cin:ai:sts=2 sw=2 ft=cpp
