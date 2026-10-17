/**
 * AirGuard AI - Peer-Consensus Drift Correction Firmware Engine (v4.0 Section 1.3)
 * Neighboring nodes in the same micro-environment cross-calibrate baseline readings
 * using peer-consensus algorithms, eliminating individual sensor drift without sending raw data to the cloud.
 */

#pragma once

#include <Arduino.h>

#define MAX_PEER_RECORDS 8

struct PeerBaselineSample {
    char  node_id[16];
    float baseline_pm25;
    float baseline_voc;
    uint32_t timestamp;
};

class PeerConsensusCalibrator {
public:
    PeerConsensusCalibrator() : peerCount(0), localOffsetPM(0.0f), localOffsetVOC(0.0f) {}

    void registerPeerReading(const char* peerId, float pm25, float voc) {
        for (int i = 0; i < peerCount; i++) {
            if (strcmp(peers[i].node_id, peerId) == 0) {
                peers[i].baseline_pm25 = pm25;
                peers[i].baseline_voc = voc;
                peers[i].timestamp = millis();
                return;
            }
        }
        if (peerCount < MAX_PEER_RECORDS) {
            strncpy(peers[peerCount].node_id, peerId, 15);
            peers[peerCount].node_id[15] = '\0';
            peers[peerCount].baseline_pm25 = pm25;
            peers[peerCount].baseline_voc = voc;
            peers[peerCount].timestamp = millis();
            peerCount++;
        }
    }

    /**
     * Calculates the median consensus baseline among peer nodes and updates zero-point offsets.
     */
    void computeConsensusOffsets(float myRawPM, float myRawVOC) {
        if (peerCount == 0) return;

        float pm_values[MAX_PEER_RECORDS + 1];
        pm_values[0] = myRawPM;
        int count = 1;

        for (int i = 0; i < peerCount; i++) {
            pm_values[count++] = peers[i].baseline_pm25;
        }

        // Simple sorting for median
        for (int i = 0; i < count - 1; i++) {
            for (int j = i + 1; j < count; j++) {
                if (pm_values[i] > pm_values[j]) {
                    float tmp = pm_values[i];
                    pm_values[i] = pm_values[j];
                    pm_values[j] = tmp;
                }
            }
        }

        float consensusMedianPM = pm_values[count / 2];
        // Smooth Kalman/alpha filter to prevent sharp step jumps:
        // offset = offset * 0.9 + (consensus - raw) * 0.1
        float targetOffset = consensusMedianPM - myRawPM;
        localOffsetPM = (localOffsetPM * 0.85f) + (targetOffset * 0.15f);

        Serial.printf("[PEER CONSENSUS] Consensus Median PM2.5: %.2f | Calibrated Local Offset: %.2f\n",
                      consensusMedianPM, localOffsetPM);
    }

    float getCalibratedPM25(float rawPM) const {
        return max(0.0f, rawPM + localOffsetPM);
    }

    float getLocalOffset() const {
        return localOffsetPM;
    }

private:
    PeerBaselineSample peers[MAX_PEER_RECORDS];
    int   peerCount;
    float localOffsetPM;
    float localOffsetVOC;
};
