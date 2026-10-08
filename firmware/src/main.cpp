/**
 * AirGuard AI - ESP32 Main Firmware Entrypoint (FR-1, FR-2, Section 2.1)
 * Enhanced with:
 * - Full multi-sensor serialization (PM, CO2, VOC, Temp, Hum, Pressure, Light, Noise, Battery, GPS)
 * - MicroSD Card permanent logging
 * - Deep Sleep Power Management for prolonged standalone deployment
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "sensors.h"
#include "display.h"
#include "offline_queue.h"

static WiFiClient espClient;
static PubSubClient mqttClient(espClient);

static SensorSuite sensors;
static FeedbackUI ui;
static OfflineQueue offlineQueue;

static unsigned long lastSampleTime = 0;
static unsigned long lastReconnectAttempt = 0;

void setupWiFi() {
    Serial.printf("[WiFi] Connecting to %s...\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String msg;
    for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
    Serial.printf("[MQTT] Inbound Command on [%s]: %s\n", topic, msg.c_str());

    if (msg.indexOf("ALARM") >= 0) {
        ui.triggerAlarm(true);
    }
}

void reconnectMQTT() {
    if (WiFi.status() != WL_CONNECTED) return;

    if (!mqttClient.connected()) {
        unsigned long now = millis();
        if (now - lastReconnectAttempt > 5000) {
            lastReconnectAttempt = now;
            Serial.print("[MQTT] Attempting broker connection...");

            if (mqttClient.connect(DEVICE_ID)) {
                Serial.println(" CONNECTED!");
                mqttClient.subscribe(MQTT_TOPIC_SUB);

                // Drain accumulated offline flash/RAM buffer (FR-2.3)
                if (offlineQueue.getPendingCount() > 0) {
                    offlineQueue.flushToMQTT(mqttClient, MQTT_TOPIC_PUB);
                }
            } else {
                Serial.printf(" FAILED, rc=%d. Retrying.\n", mqttClient.state());
            }
        }
    }
}

String serializeTelemetry(const SensorReadings &r) {
    JsonDocument doc;
    doc["device_id"]        = DEVICE_ID;
    doc["room"]             = DEVICE_ROOM;
    doc["uptime_ms"]        = millis();
    doc["pm1_0"]            = r.pm1_0;
    doc["pm2_5"]            = r.pm2_5;
    doc["pm10"]             = r.pm10;
    doc["co2"]              = r.co2_ppm;
    doc["voc"]              = r.voc_ppb;
    doc["temperature"]      = r.temperature_c;
    doc["humidity"]         = r.humidity_rh;
    doc["pressure"]         = r.pressure_hpa;
    doc["ambient_light"]    = r.ambient_light_lux;
    doc["noise_level"]      = r.noise_level_db;
    doc["battery_voltage"]  = r.battery_voltage;
    doc["battery_pct"]      = r.battery_pct;
    doc["latitude"]         = r.latitude;
    doc["longitude"]        = r.longitude;

    String jsonOutput;
    serializeJson(doc, jsonOutput);
    return jsonOutput;
}

int estimateLocalAQI(float pm25, int co2) {
    int aqi_pm = (int)(pm25 * 3.0);
    int aqi_co2 = co2 > 1000 ? (int)((co2 - 1000) * 0.15 + 100) : 50;
    return max(aqi_pm, aqi_co2);
}

const char* getAQILabel(int aqi) {
    if (aqi <= 50) return "GOOD";
    if (aqi <= 100) return "MODERATE";
    if (aqi <= 150) return "SENSITIVE";
    if (aqi <= 200) return "UNHEALTHY";
    return "HAZARD";
}

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n==========================================");
    Serial.println("  AirGuard AI - Edge Node (v1.3 Expanded) ");
    Serial.println("==========================================");

    sensors.begin();
    ui.begin();
    offlineQueue.begin();

    setupWiFi();
    mqttClient.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
    mqttClient.setCallback(mqttCallback);

    Serial.println("[AirGuard AI] Setup complete. Entering operational loop.");
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        if (!mqttClient.connected()) {
            reconnectMQTT();
        } else {
            mqttClient.loop();
        }
    }

    unsigned long currentMillis = millis();

    if (currentMillis - lastSampleTime >= TELEMETRY_INTERVAL_MS) {
        lastSampleTime = currentMillis;

        SensorReadings readings = sensors.readAll();
        String jsonPayload = serializeTelemetry(readings);

        bool published = false;
        if (mqttClient.connected()) {
            published = mqttClient.publish(MQTT_TOPIC_PUB, jsonPayload.c_str());
        }

        if (!published) {
            // Buffer locally during network dropouts (FR-2.3, NFR-2)
            offlineQueue.enqueue(jsonPayload);
        }

        int estimatedAQI = estimateLocalAQI(readings.pm2_5, readings.co2_ppm);
        const char* label = getAQILabel(estimatedAQI);

        ui.update(
            readings,
            estimatedAQI,
            label,
            WiFi.status() == WL_CONNECTED,
            mqttClient.connected(),
            offlineQueue.getPendingCount()
        );

        if (readings.pm2_5 > 55.0 || readings.co2_ppm > 1600 || readings.voc_ppb > 600) {
            ui.triggerAlarm(false);
        }

        // Section 2.1 Power Optimization: if operating on low battery (< 15%), enter deep sleep
        if (readings.battery_pct < 15 && readings.battery_voltage < 3.4) {
            Serial.printf("[Power] Critical battery (%d%%). Entering deep sleep for %ds...\n", readings.battery_pct, BATTERY_SAVER_SLEEP_S);
            esp_sleep_enable_timer_wakeup(BATTERY_SAVER_SLEEP_S * 1000000ULL);
            esp_deep_sleep_start();
        }
    }
}
