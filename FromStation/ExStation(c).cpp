/*
 * CHS MQTT : Smart Farm
 */

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>
#include <String.h>


const char* ssid = "iPhone Tony";
const char* password = "09090909";
const char* mqtt_server = "172.20.10.2";
#define mqtt_port 1883 // เลข port
#define mqtt_user "nud-11" // user
#define mqtt_password "iot1234" // password

WiFiClient espClient;
PubSubClient client(espClient);
int moisture_value = 0;
void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
 
  }
  

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect("Tony", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      // ... and resubscribe
      client.subscribe("rainy");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 3 seconds before retrying
      delay(3000);
    }
  }
}


int sensor_value;
bool LED_status = HIGH;
int currantMillis = 0;
int counter = 0;
int previousMillis = 0;
int pulse = 0;

void setup() {
 
//  
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  pinMode(D0,INPUT);
  pinMode(A0,INPUT);
  

  //Mega2560.begin(9600);
  

// put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(D2, INPUT_PULLUP);
  Serial.begin(9600);
//  Timer1.initialize(1000);
//  Timer1.pwm(outPin)
//  attachInterrupt(digitalPinToInterrupt (D2),countPulse, FALLING);

}
void countPulse()
{
  counter++;
//  Serial.println(counter);
}
char* toCharArray(String str) {
  return &str[0];
}
void loop() {
  
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
//  sensor_value = digitalRead(D0);
//  if (sensor_value==HIGH){
//    client.publish("rainy", "station2/RAIN");
//    delay(1000);
//  }

// put your main code here, to run repeatedly:
  currantMillis = millis();
  counter = pulseIn(D2, HIGH);
//  Serial.println(counter);  
  delay(10);
  if (counter > 0){
    pulse++;
  }
  
  if(currantMillis - previousMillis >= 5000){ 
    counter = 0;
    Serial.println(pulse);
    moisture_value = analogRead(A0);
    String stringOne = "{\"day\":"+String(pulse)+", \"humidity\":"+String(moisture_value)+",\"stationname\":\"C\"}";
    client.publish("rainy", toCharArray(stringOne));
    pulse = 0;
    previousMillis = currantMillis;
    LED_status = !LED_status;
    digitalWrite(LED_BUILTIN, !LED_status);
  }
}
