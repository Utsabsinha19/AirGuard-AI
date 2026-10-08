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
#include "tinyml_infer.h"

static WiFiClient espClient;
static PubSubClient mqttClient(espClient);

static SensorSuite sensors;
static FeedbackUI ui;
static OfflineQueue offlineQueue;
static TinyMLEdgeClassifier tinyml;

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

                // Drain accumulated offline flash/RAM buffer (FR-2.3, Section 1.2)
                if (offlineQueue.getPendingCount() > 0) {
                    offlineQueue.flushToMQTT(mqttClient, MQTT_TOPIC_PUB_V3);
                }
            } else {
                Serial.printf(" FAILED, rc=%d. Retrying.\n", mqttClient.state());
            }
        }
    }
}

String serializeTelemetry(const SensorReadings &r, const TinyMLInferenceResult &mlRes) {
    JsonDocument doc;
    doc["device_id"]        = DEVICE_ID;
    doc["location"]         = DEVICE_ROOM;
    doc["zone"]             = DEVICE_ZONE;
    doc["firmware_version"] = FIRMWARE_VERSION;
    doc["uptime_ms"]        = millis();

    // v3.0 Nested metrics format
    JsonObject metrics      = doc["metrics"].to<JsonObject>();
    metrics["pm0_3"]        = r.pm0_3;
    metrics["pm1_0"]        = r.pm1_0;
    metrics["pm2_5"]        = r.pm2_5;
    metrics["pm10"]         = r.pm10;
    metrics["co2"]          = r.co2_ppm;
    metrics["voc"]          = r.voc_ppb;
    metrics["hcho"]         = r.hcho_ppm;
    metrics["voc_index"]    = r.voc_index;
    metrics["nox_index"]    = r.nox_index;
    metrics["gas_resistance"] = r.gas_resistance_ohms;
    metrics["temperature"]  = r.temperature_c;
    metrics["humidity"]     = r.humidity_rh;
    metrics["pressure"]     = r.pressure_hpa;
    metrics["battery_pct"]  = r.battery_pct;

    // TinyML Edge Diagnostics
    JsonObject edgeML       = doc["edge_tinyml"].to<JsonObject>();
    edgeML["anomaly"]       = mlRes.is_anomaly;
    edgeML["anomaly_score"] = mlRes.anomaly_score;
    edgeML["diagnosed_cause"] = mlRes.diagnosed_cause;
    edgeML["relay_active"]  = mlRes.trigger_local_relay;

    // Top-level fields for flat backward compatibility
    doc["pm0_3"]            = r.pm0_3;
    doc["pm1_0"]            = r.pm1_0;
    doc["pm2_5"]            = r.pm2_5;
    doc["pm10"]             = r.pm10;
    doc["co2"]              = r.co2_ppm;
    doc["voc"]              = r.voc_ppb;
    doc["hcho"]             = r.hcho_ppm;
    doc["voc_index"]        = r.voc_index;
    doc["nox_index"]        = r.nox_index;
    doc["gas_resistance"]   = r.gas_resistance_ohms;
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
    Serial.println("  AirGuard AI - Edge Node (v3.0-PRO)      ");
    Serial.println("  TinyML On-Device + Matter Smart Relay   ");
    Serial.println("==========================================");

    pinMode(RELAY_ACTUATOR_PIN, OUTPUT);
    digitalWrite(RELAY_ACTUATOR_PIN, LOW);

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

        // v3.0 TinyML On-Device Edge Inference (< 15ms zero-latency)
        TinyMLFeatures feat;
        feat.pm2_5 = readings.pm2_5;
        feat.pm10 = readings.pm10;
        feat.co2 = readings.co2_ppm;
        feat.voc = readings.voc_ppb;
        feat.hcho = readings.hcho_ppm;
        feat.temperature = readings.temperature_c;
        feat.humidity = readings.humidity_rh;
        feat.pressure = readings.pressure_hpa;

        TinyMLInferenceResult mlRes = tinyml.predict(feat);

        // Zero-latency local relay actuation without Wi-Fi round-trip
        digitalWrite(RELAY_ACTUATOR_PIN, mlRes.trigger_local_relay ? HIGH : LOW);

        String jsonPayload = serializeTelemetry(readings, mlRes);

        bool published = false;
        if (mqttClient.connected()) {
            published = mqttClient.publish(MQTT_TOPIC_PUB_V3, jsonPayload.c_str());
            if (!published) {
                published = mqttClient.publish(MQTT_TOPIC_PUB_V2, jsonPayload.c_str());
            }
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

        if (mlRes.is_anomaly || readings.pm2_5 > 55.0 || readings.co2_ppm > 1600 || readings.voc_ppb > 600) {
            ui.triggerAlarm(false);
        }

        // Section 1.3: Interrupt-driven threshold wakeups & adaptive deep sleep
        if (readings.battery_pct < 25) {
            Serial.printf("[Power] Standalone battery power (%d%%). Enabling hazard interrupt on PIN %d & sleeping %ds...\n",
                          readings.battery_pct, PIN_HAZARD_INT, BATTERY_SAVER_SLEEP_S);
            esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_HAZARD_INT, 1);
            esp_sleep_enable_timer_wakeup(BATTERY_SAVER_SLEEP_S * 1000000ULL);
            esp_deep_sleep_start();
        }
    }
}
