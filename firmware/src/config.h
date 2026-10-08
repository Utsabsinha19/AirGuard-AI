/**
 * AirGuard AI - ESP32 Hardware Pinouts & Network Configuration (FR-1, FR-2)
 */

#pragma once

#include <Arduino.h>

// ==========================================
// Device Identity
// ==========================================
#define DEVICE_ID           "AG-001"
#define DEVICE_ROOM         "Master Bedroom"
#define FIRMWARE_VERSION    "v1.2.0"

// ==========================================
// Wi-Fi & MQTT Broker Configuration
// ==========================================
#define WIFI_SSID           "Your_WiFi_SSID"
#define WIFI_PASSWORD       "Your_WiFi_Password"

#define MQTT_BROKER_HOST    "192.168.1.100"   // Backend IP or EMQX Cloud
#define MQTT_BROKER_PORT    1883
#define MQTT_TOPIC_PUB      "airguard/" DEVICE_ID "/telemetry"
#define MQTT_TOPIC_SUB      "airguard/" DEVICE_ID "/command"

// ==========================================
// Hardware Pinout Definitions (ESP32)
// ==========================================
// I2C Bus (SHT31 @ 0x44, SGP30 @ 0x58, SSD1306 OLED @ 0x3C)
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

// Battery Voltage ADC Monitor (FR-1.4)
#define BATTERY_ADC_PIN     34

// ==========================================
// Timing & Sampling Constants
// ==========================================
#define TELEMETRY_INTERVAL_MS   2000    // Stream every 2 seconds (FR-1.1, US-01)
#define MAX_OFFLINE_QUEUE_ITEMS 500     // SPI Flash buffer entries (FR-2.3)
