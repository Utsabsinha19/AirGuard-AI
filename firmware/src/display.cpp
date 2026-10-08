/**
 * AirGuard AI - Feedback UI Driver Implementation (FR-1.3)
 */

#include "display.h"
#include "config.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C

static Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

FeedbackUI::FeedbackUI() {}

bool FeedbackUI::begin() {
    pinMode(RGB_RED_PIN, OUTPUT);
    pinMode(RGB_GREEN_PIN, OUTPUT);
    pinMode(RGB_BLUE_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    digitalWrite(BUZZER_PIN, LOW);
    setRGBColor(0, 0, 0);

    if (!oled.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
        Serial.println("[Display] OLED allocation failed");
        return false;
    }

    oled.clearDisplay();
    oled.setTextColor(SSD1306_WHITE);
    oled.setTextSize(1);
    oled.setCursor(18, 15);
    oled.print("AirGuard AI");
    oled.setCursor(10, 32);
    oled.print("Initializing IoT...");
    oled.display();
    return true;
}

void FeedbackUI::setRGBColor(uint8_t r, uint8_t g, uint8_t b) {
    analogWrite(RGB_RED_PIN, r);
    analogWrite(RGB_GREEN_PIN, g);
    analogWrite(RGB_BLUE_PIN, b);
}

void FeedbackUI::setAQIColor(int aqi) {
    if (aqi <= 50) {
        setRGBColor(0, 255, 60);      // Emerald Green
    } else if (aqi <= 100) {
        setRGBColor(255, 200, 0);    // Amber Yellow
    } else if (aqi <= 150) {
        setRGBColor(255, 100, 0);    // Orange
    } else if (aqi <= 200) {
        setRGBColor(255, 20, 20);    // Crimson Red
    } else {
        setRGBColor(180, 0, 255);    // Hazardous Purple
    }
}

void FeedbackUI::update(
    const SensorReadings &readings,
    int aqi,
    const char* aqiCategory,
    bool wifiConnected,
    bool mqttConnected,
    int queueCount
) {
    setAQIColor(aqi);

    oled.clearDisplay();

    // Top status bar
    oled.setTextSize(1);
    oled.setCursor(0, 0);
    oled.printf("%s", DEVICE_ID);

    oled.setCursor(55, 0);
    if (queueCount > 0) {
        oled.printf("BUF:%d", queueCount);
    } else {
        oled.print(mqttConnected ? "MQTT:OK" : (wifiConnected ? "NO-MQTT" : "OFFLINE"));
    }

    // Horizontal line
    oled.drawLine(0, 10, 127, 10, SSD1306_WHITE);

    // Large AQI Display
    oled.setTextSize(2);
    oled.setCursor(0, 14);
    oled.printf("AQI %d", aqi);

    oled.setTextSize(1);
    oled.setCursor(80, 18);
    oled.print(aqiCategory);

    // Sub-pollutant grid
    oled.setCursor(0, 34);
    oled.printf("PM2.5: %.1f ug", readings.pm2_5);

    oled.setCursor(0, 44);
    oled.printf("CO2: %d ppm", readings.co2_ppm);

    oled.setCursor(0, 54);
    oled.printf("VOC: %d ppb", readings.voc_ppb);

    // Temp & Humidity column on right
    oled.setCursor(82, 36);
    oled.printf("%.1f C", readings.temperature_c);

    oled.setCursor(82, 48);
    oled.printf("%.0f%% RH", readings.humidity_rh);

    oled.display();
}

void FeedbackUI::triggerAlarm(bool critical) {
    if (critical) {
        // Urgent alternating tone
        for (int i = 0; i < 3; i++) {
            digitalWrite(BUZZER_PIN, HIGH);
            delay(120);
            digitalWrite(BUZZER_PIN, LOW);
            delay(80);
        }
    } else {
        // Gentle single beep
        digitalWrite(BUZZER_PIN, HIGH);
        delay(100);
        digitalWrite(BUZZER_PIN, LOW);
    }
}
