#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>
#include "Adafruit_VL53L0X.h"

// Replace with your network credentials
const char* ssid = "SpectrumSetup-DB";
const char* password = "errandnoble217";

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);
// Create a WebSocket object
AsyncWebSocket ws("/ws");

// Create VL53L0X object
Adafruit_VL53L0X lox = Adafruit_VL53L0X();



void sendDistance() {
  if (lox.isRangeComplete()) {
    int distance = lox.readRange();
    int distance2 = random(distance - 10, distance + 10);
    String message = String(distance) + String(",") + String(distance2);
    // Send the distance to all connected WebSocket clients
    ws.textAll(message);
    Serial.println(message);
  }
}

// WebSocket event handler
void onWebSocketEvent(AsyncWebSocket * server, AsyncWebSocketClient * client, 
                      AwsEventType type, void * arg, uint8_t *data, size_t len) {
  if (type == WS_EVT_CONNECT) {
    Serial.println("Client connected");
  } else if (type == WS_EVT_DISCONNECT) {
    Serial.println("Client disconnected");
  }
}

void setup() {
  // Start Serial communication
  Serial.begin(115200);

  randomSeed(analogRead(0));  // Use an analog pin to seed random number generator

  while (!Serial){
    ;
  }
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  // Print the IP address where the ESP32 is running
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  // Start VL53L0X sensor
  if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X"));
    while (1);
  }

  // Start continuous ranging
  lox.startRangeContinuous(10); //10 for 10 ms intermeasurement period
  Serial.println("VL53L0X ranging started");

  // Register WebSocket event handler
  ws.onEvent(onWebSocketEvent);
  // Attach WebSocket to the server
  server.addHandler(&ws);

  // Start the server
  server.begin();
  Serial.println("WebSocket server started");
}

void loop() {
  // Send the distance measurement over WebSocket
  sendDistance();

  // Handle WebSocket events
  ws.cleanupClients();

  // Add a delay to avoid flooding WebSocket with messages too quickly
  delay(5); // Adjust delay as needed
}
