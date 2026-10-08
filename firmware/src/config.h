/**
 * AirGuard AI - ESP32 Hardware Pinouts & Network Configuration (FR-1, FR-2, Section 2.1)
 * Enhanced with Optional Hardware Expansion Modules:
 * - BMP280 Barometric Pressure & Altitude
 * - NEO-6M GPS Spatial Tracking
 * - Ambient Light & Acoustic Noise Sensors
 * - MicroSD Card SPI Offline Data Logging
 * - Li-Po Battery Monitoring & Deep Sleep Power Management
 */

#pragma once

#include <Arduino.h>

// ==========================================
// Device Identity & Room Location
// ==========================================
#define DEVICE_ID           "AG-001"
#define DEVICE_ROOM         "Master Bedroom"
#define DEVICE_ZONE         "Bedroom"
#define FIRMWARE_VERSION    "v3.0.0-PRO"

// ==========================================
// Wi-Fi & MQTT Broker Configuration
// ==========================================
#define WIFI_SSID           "Your_WiFi_SSID"
#define WIFI_PASSWORD       "Your_WiFi_Password"

#define MQTT_BROKER_HOST    "192.168.1.100"   // Backend IP or EMQX Cloud
#define MQTT_BROKER_PORT    1883
#define MQTT_TOPIC_PUB      "airguard/" DEVICE_ID "/telemetry"
#define MQTT_TOPIC_PUB_V2   "airguard/v1/devices/" DEVICE_ID "/telemetry"
#define MQTT_TOPIC_PUB_V3   "airguard/v3/devices/" DEVICE_ID "/telemetry"
#define MQTT_TOPIC_SUB      "airguard/" DEVICE_ID "/command"

// Hardware Interrupt Wakeup & Smart Home Relay (v3.0 Section 1.2, 1.3)
#define PIN_HAZARD_INT      33
#define RELAY_ACTUATOR_PIN  4

// ==========================================
// Primary Sensor Pinout Definitions (ESP32)
// ==========================================
// Shared I2C Bus (SHT31 @ 0x44, SGP30 @ 0x58, BMP280 @ 0x76, SSD1306 @ 0x3C)
#define I2C_SDA_PIN         21
#define I2C_SCL_PIN         22

// UART1: PMS5003 Laser Particulate Sensor
#define PMS_RX_PIN          16
#define PMS_TX_PIN          17

// UART2: MH-Z19B NDIR CO2 Sensor
#define MHZ_RX_PIN          25
#define MHZ_TX_PIN          26

// Visual & Audio Local Feedback (FR-1.3)
#define RGB_RED_PIN         12
#define RGB_GREEN_PIN       14
#define RGB_BLUE_PIN        27
#define BUZZER_PIN          13

// ==========================================
// Expanded Hardware Modules (Section 2.1)
// ==========================================
// Ambient Light Sensor (TEMT6000 / Photodiode ADC)
#define AMBIENT_LIGHT_ADC   35

// Indoor Acoustic / Noise Sensor (Microphone ADC)
#define NOISE_SENSOR_ADC    32

// Battery Voltage Divider Monitor (3.7V Li-Po via 2x100k divider)
#define BATTERY_ADC_PIN     34

// MicroSD Card Module SPI
#define SD_CS_PIN           5
#define SD_MOSI_PIN         23
#define SD_MISO_PIN         19
#define SD_SCK_PIN          18

// GPS Module (NEO-6M SoftwareSerial or UART3)
#define GPS_RX_PIN          4
#define GPS_TX_PIN          2

// ==========================================
// Power Management & Timing Constants
// ==========================================
#define TELEMETRY_INTERVAL_MS   2000    // Normal sampling interval (2s)
#define BATTERY_SAVER_SLEEP_S   60      // Deep sleep interval when battery powered
#define MAX_OFFLINE_QUEUE_ITEMS 500     // In-memory circular buffer count
#define SD_LOG_FILE             "/airguard_data.csv"
