#include <SoftwareSerial.h>
//
#define echoPin 6 // attach pin D6 Arduino to pin Echo of HC-SR04
#define trigPin 5 //attach pin D6 Arduino to pin Trig of HC-SR04
//
int RX_pin=11; //define pin 11 as RX
int TX_pin=12; //define pin 12 as TX

SoftwareSerial BTserial(RX_pin,TX_pin);
String BT_data;
String Arduino_data;

long duration; // variable for the duration of sound wave travel
int distance; // variable for the distance measurement
int Power = 4; //  the pin in charge of powering the ultrasound   


void setup(){
  Serial.begin(9600);// Serial Communication is starting with 9600 of baudrate speed
  BTserial.begin(9600);// Bluetooth Serial Communication is starting with 9600 of baudrate speed

  pinMode(trigPin, OUTPUT); // Sets the trigPin as an OUTPUT
  pinMode(echoPin, INPUT); // Sets the echoPin as an INPUT
  pinMode(Power, OUTPUT);     
  digitalWrite(Power, HIGH);  
}

void loop(){
 // Clears the trigPin condition
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin HIGH (ACTIVE) for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and back)
  // Displays the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if ( distance< 20){ //If Distance is less than 20 cm
        BTserial.println("1"); // write a 1 on the receiver's end (in our case in the Raspberry Pi)
        Serial.println("Sending bluetooth signal"); // write in the serial port a 1 
  }
  delay(1000);
  }
