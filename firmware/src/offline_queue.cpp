/**
 * AirGuard AI - Offline Queuing Implementation (FR-2.3, NFR-2)
 */

#include "offline_queue.h"

OfflineQueue::OfflineQueue() : head(0), tail(0), count(0) {}

bool OfflineQueue::begin() {
    head = 0;
    tail = 0;
    count = 0;
    Serial.println("[OfflineQueue] Circular buffer initialized.");
    return true;
}

bool OfflineQueue::enqueue(const String &jsonPayload) {
    if (count >= MAX_RAM_BUFFER) {
        // Buffer full: overwrite oldest record (circular FIFO behavior)
        tail = (tail + 1) % MAX_RAM_BUFFER;
        count--;
    }

    buffer[head] = jsonPayload;
    head = (head + 1) % MAX_RAM_BUFFER;
    count++;

    Serial.printf("[OfflineQueue] Enqueued offline telemetry. Pending: %d\n", count);
    return true;
}

int OfflineQueue::getPendingCount() {
    return count;
}

int OfflineQueue::flushToMQTT(PubSubClient &client, const char* topic) {
    if (count == 0 || !client.connected()) {
        return 0;
    }

    Serial.printf("[OfflineQueue] Flushing %d buffered telemetry records to broker...\n", count);
    int flushed = 0;

    while (count > 0 && client.connected()) {
        String payload = buffer[tail];
        if (client.publish(topic, payload.c_str())) {
            tail = (tail + 1) % MAX_RAM_BUFFER;
            count--;
            flushed++;
            delay(15); // gentle pacing to avoid socket congestion
        } else {
            Serial.println("[OfflineQueue] Publish failed during flush, aborting batch.");
            break;
        }
    }

    Serial.printf("[OfflineQueue] Successfully flushed %d records. Remaining: %d\n", flushed, count);
    return flushed;
}
