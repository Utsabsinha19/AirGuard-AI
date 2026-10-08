/**
 * AirGuard AI - OLED Display, RGB LED & Buzzer Feedback Interface (FR-1.3)
 */

#pragma once

#include <Arduino.h>
#include "sensors.h"

class FeedbackUI {
public:
    FeedbackUI();
    bool begin();
    void update(const SensorReadings &readings, int aqi, const char* aqiCategory, bool wifiConnected, bool mqttConnected, int queueCount);
    void triggerAlarm(bool critical);

private:
    void setRGBColor(uint8_t r, uint8_t g, uint8_t b);
    void setAQIColor(int aqi);
};
