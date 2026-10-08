/**
 * AirGuard AI - Offline Queuing Protocol (FR-2.3, NFR-2)
 * Manages resilient circular FIFO storage on SPI Flash during network drops,
 * automatically executing sequential flushing upon Wi-Fi / MQTT reconnection.
 */

#pragma once

#include <Arduino.h>
#include <PubSubClient.h>

class OfflineQueue {
public:
    OfflineQueue();
    bool begin();
    bool enqueue(const String &jsonPayload);
    int  getPendingCount();
    int  flushToMQTT(PubSubClient &client, const char* topic);

private:
    static const int MAX_RAM_BUFFER = 256;
    String buffer[MAX_RAM_BUFFER];
    int head;
    int tail;
    int count;
};
