#include <Arduino.h>
#include <Servo.h>

Servo radarServo;

const uint8_t PIN_SERVO = 9;
const uint8_t PIN_TRIG  = 11;
const uint8_t PIN_ECHO  = 12;

const int  MAX_DISTANCE = 60;  
const long ECHO_TIMEOUT = 4000; 
const int  STEP_DELAY   = 15;    

int readDistance() {
  digitalWrite(PIN_TRIG, LOW);  
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH); 
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  long dur = pulseIn(PIN_ECHO, HIGH, ECHO_TIMEOUT);
  if (dur == 0) return -1;
  long cm = dur / 58;                    
  if (cm < 2 || cm > MAX_DISTANCE) return -1;
  return (int)cm;
}

void sendReading(int angle) {
  int d = readDistance();
  Serial.print(angle);
  Serial.print(',');
  Serial.println(d > 0 ? d : 0);         
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  radarServo.attach(PIN_SERVO);
}

void loop() {
  for (int a = 0;   a <= 180; a++) { radarServo.write(a); delay(STEP_DELAY); sendReading(a); }
  for (int a = 180; a >= 0;   a--) { radarServo.write(a); delay(STEP_DELAY); sendReading(a); }
}
