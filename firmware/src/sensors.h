/**
 * AirGuard AI - Sensor Suite Abstraction Layer (FR-1.2)
 * Interfaces: PMS5003 (Particulate), MH-Z19B (NDIR CO2), SGP30 (VOC), SHT31 (Temp/Hum)
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
    bool  is_valid;
};

class SensorSuite {
public:
    SensorSuite();
    bool begin();
    SensorReadings readAll();

private:
    bool initPMS5003();
    bool initMHZ19();
    bool initSGP30();
    bool initSHT31();

    bool readPMS(float &pm1_0, float &pm2_5, float &pm10);
    int  readCO2();
    int  readVOC();
    bool readTempHumidity(float &temp, float &hum);
};
