#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"

// WiFi Access Point credentials
const char *ssid = "XIAO_ESP32_AP";
const char *password = ""; // Open network

// Create an instance of the asynchronous web server running on port 80
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");  // WebSocket endpoint at /ws

// Create an instance of the sensor
MAX30105 particleSensor;

void sendSensorData() {
    const int numSamples = 500;
    int redArray[numSamples];
    int irArray[numSamples];

    // Collect 500 samples
    for (int i = 0; i < numSamples; i++) {
        redArray[i] = particleSensor.getRed();
        irArray[i]  = particleSensor.getIR();
        delay(1); // Small delay to ensure valid readings
    }

    // Build JSON response efficiently
    String jsonResponse;
    jsonResponse.reserve(16000); // Preallocate memory to prevent fragmentation
    jsonResponse += "{\"red\":[";

    for (int i = 0; i < numSamples; i++) {
        jsonResponse += String(redArray[i]);
        if (i < numSamples - 1) jsonResponse += ",";
    }
    jsonResponse += "],\"ir\":[";

    for (int i = 0; i < numSamples; i++) {
        jsonResponse += String(irArray[i]);
        if (i < numSamples - 1) jsonResponse += ",";
    }
    jsonResponse += "]}";

    // Send JSON via WebSocket to all connected clients
    ws.textAll(jsonResponse);
}

// WebSocket event handler
void onWebSocketEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, 
                      void *arg, uint8_t *data, size_t len) {
    if (type == WS_EVT_CONNECT) {
        Serial.printf("Client %u connected\n", client->id());
    } else if (type == WS_EVT_DISCONNECT) {
        Serial.printf("Client %u disconnected\n", client->id());
    }
}

void setup() {
    Serial.begin(115200);
    while (!Serial) { }

    Serial.println("Starting Access Point and initializing sensor...");

    // Start WiFi in Access Point mode
    WiFi.softAP(ssid, password);
    IPAddress IP = WiFi.softAPIP();
    Serial.print("Access Point Started! IP Address: ");
    Serial.println(IP);

    // Initialize I2C communication with the correct pins for your Xiao ESP32C3.
    Wire.begin(D4, D5); // Example: SDA on D4, SCL on D5

    // Initialize MAX30102 sensor
    if (!particleSensor.begin(Wire)) {
        Serial.println("MAX30102 not found. Check wiring.");
        while (1);
    }

    // Set up sensor settings
    particleSensor.setup(); // Use default settings
    particleSensor.setPulseAmplitudeRed(0x1F);
    particleSensor.setPulseAmplitudeIR(0x1F);

    Serial.println("MAX30102 sensor initialized.");

    // Welcome endpoint
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send(200, "text/plain", "ESP32 AP with MAX30102 Sensor & WebSockets");
    });

    // Attach WebSocket event handler and start the server
    ws.onEvent(onWebSocketEvent);
    server.addHandler(&ws);
    server.begin();
}

void loop() {
    ws.cleanupClients();  // Manage WebSocket connections
    sendSensorData();     // Send sensor data periodically
    delay(1000);          // Adjust delay based on data rate needs
}
