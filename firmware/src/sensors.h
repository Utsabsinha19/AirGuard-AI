/**
 * AirGuard AI - Sensor Suite Abstraction Layer (FR-1.2, Section 2.1)
 * Interfaces:
 * - PMS5003 (Particulate Matter PM1.0, PM2.5, PM10)
 * - MH-Z19B (NDIR Carbon Dioxide)
 * - SGP30 (Metal-Oxide VOC Array)
 * - SHT31 (Temperature & Humidity)
 * - BMP280 (Barometric Air Pressure & Weather Altitude)
 * - TEMT6000 / ADC (Ambient Lux Light)
 * - Microphone / ADC (Acoustic Noise dB)
 * - Battery ADC (Li-Po Voltage & Remaining Percentage)
 * - NEO-6M (GPS Latitude, Longitude)
 */

#pragma once

#include <Arduino.h>

struct SensorReadings {
    float pm1_0;
    float pm2_5;
    float pm10;
    int   co2_ppm;
    int   voc_ppb;
    float temperature_c;
    float humidity_rh;
    
    // Expanded sensor suite
    float pressure_hpa;
    float altitude_m;
    float ambient_light_lux;
    float noise_level_db;
    float battery_voltage;
    int   battery_pct;
    float latitude;
    float longitude;

    bool  is_valid;
};

class SensorSuite {
public:
    SensorSuite();
    bool begin();
    SensorReadings readAll();
    bool logToSDCard(const SensorReadings &r);

private:
    bool initPMS5003();
    bool initMHZ19();
    bool initSGP30();
    bool initSHT31();
    bool initBMP280();
    bool initSDCard();

    bool readPMS(float &pm1_0, float &pm2_5, float &pm10);
    int  readCO2();
    int  readVOC();
    bool readTempHumidity(float &temp, float &hum);
    bool readBarometric(float &pressure, float &altitude);
    float readAmbientLight();
    float readNoiseLevel();
    void  readBattery(float &voltage, int &percentage);
    void  readGPS(float &lat, float &lon);

    bool sdCardAvailable;
};
