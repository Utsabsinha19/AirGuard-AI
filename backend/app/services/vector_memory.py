"""
AirGuard AI - Hybrid Storage & Vector Database Incident Memory (v4.0 Section 4.1)
Contextual embedding engine enabling semantic similarity search over historical
environmental incidents, industrial contamination events, and building recovery playbooks.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np


class IncidentVectorMemoryEngine:
    """
    Vector similarity search engine for environmental incident memory (Qdrant / Milvus abstraction).
    """
    def __init__(self):
        # Seeded historical incident memory library
        self.incident_index: List[Dict[str, Any]] = [
            {
                "incident_id": "INC-2026-0812-01",
                "timestamp": (datetime.utcnow() - timedelta(days=64)).isoformat(),
                "incident_type": "INDOOR_SEARING_FRYING",
                "sensor_signature": {
                    "pm2_5": 88.5,
                    "co2": 620.0,
                    "voc": 340.0,
                    "hcho": 0.02,
                    "acoustic_db": 68.5,
                    "temperature": 24.5
                },
                "resolution_strategy": "Direct relay pin 4 trigger -> Kitchen range hood max + living room HEPA booster. Isolated interior doors.",
                "time_to_recover_mins": 14.5
            },
            {
                "incident_id": "INC-2026-0904-03",
                "timestamp": (datetime.utcnow() - timedelta(days=42)).isoformat(),
                "incident_type": "STRUCTURAL_OFF_GASSING",
                "sensor_signature": {
                    "pm2_5": 11.2,
                    "co2": 580.0,
                    "voc": 480.0,
                    "hcho": 0.125,
                    "acoustic_db": 39.0,
                    "temperature": 23.0
                },
                "resolution_strategy": "Automated ERV fresh-air damper opened to 75% + active carbon scrubber engaged.",
                "time_to_recover_mins": 42.0
            },
            {
                "incident_id": "INC-2026-0928-02",
                "timestamp": (datetime.utcnow() - timedelta(days=18)).isoformat(),
                "incident_type": "OCCUPANCY_STAGNATION",
                "sensor_signature": {
                    "pm2_5": 14.0,
                    "co2": 1640.0,
                    "voc": 310.0,
                    "hcho": 0.03,
                    "acoustic_db": 64.0,
                    "temperature": 23.8
                },
                "resolution_strategy": "BACnet VAV supply damper boosted by 40% + cross-ventilation corridor door opened.",
                "time_to_recover_mins": 22.0
            },
            {
                "incident_id": "INC-2026-1002-04",
                "timestamp": (datetime.utcnow() - timedelta(days=14)).isoformat(),
                "incident_type": "REGIONAL_WILDFIRE_INGRESS",
                "sensor_signature": {
                    "pm2_5": 115.0,
                    "co2": 710.0,
                    "voc": 190.0,
                    "hcho": 0.04,
                    "acoustic_db": 42.0,
                    "temperature": 21.0
                },
                "resolution_strategy": "100% recirculation mode + standalone HEPA scrubbers set to Boost. Window seals locked.",
                "time_to_recover_mins": 38.0
            },
            {
                "incident_id": "INC-2026-1011-01",
                "timestamp": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                "incident_type": "HVAC_FILTER_SATURATION",
                "sensor_signature": {
                    "pm2_5": 28.5,
                    "co2": 690.0,
                    "voc": 140.0,
                    "hcho": 0.025,
                    "acoustic_db": 46.0,
                    "temperature": 22.2
                },
                "resolution_strategy": "Clogged filter notification dispatched; MERV 13 cartridge swapped; CADR restored to 260 CFM.",
                "time_to_recover_mins": 60.0
            }
        ]

    def _embed(self, sig: Dict[str, float]) -> np.ndarray:
        """
        Maps multi-sensor readings into a normalized 6-dimensional feature embedding.
        [norm_pm25, norm_co2, norm_voc, norm_hcho, norm_noise, norm_temp]
        """
        v = np.array([
            float(sig.get("pm2_5", 10.0)) / 100.0,
            float(sig.get("co2", 600.0)) / 2000.0,
            float(sig.get("voc", 100.0)) / 500.0,
            float(sig.get("hcho", 0.02)) / 0.15,
            float(sig.get("acoustic_db", 40.0)) / 100.0,
            float(sig.get("temperature", 22.0)) / 40.0
        ], dtype=float)
        norm = np.linalg.norm(v)
        return v / (norm if norm > 0 else 1.0)

    def search_similar_incidents(
        self,
        query_sig: Dict[str, float],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Finds the top-K historically matched incidents using cosine similarity.
        """
        q_vec = self._embed(query_sig)
        results = []

        for inc in self.incident_index:
            inc_vec = self._embed(inc["sensor_signature"])
            # Cosine similarity
            cosine_sim = float(np.dot(q_vec, inc_vec))
            sim_pct = round(max(0.0, min(1.0, cosine_sim)), 3)

            results.append({
                "incident_id": inc["incident_id"],
                "timestamp": inc["timestamp"],
                "incident_type": inc["incident_type"],
                "similarity_score": sim_pct,
                "sensor_signature": inc["sensor_signature"],
                "resolution_strategy": inc["resolution_strategy"],
                "time_to_recover_mins": inc["time_to_recover_mins"]
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    def index_incident(
        self,
        incident_id: str,
        incident_type: str,
        sensor_signature: Dict[str, float],
        resolution_strategy: str,
        time_to_recover_mins: float
    ):
        """
        Stores an incident in the memory index.
        """
        self.incident_index.append({
            "incident_id": incident_id,
            "timestamp": datetime.utcnow().isoformat(),
            "incident_type": incident_type,
            "sensor_signature": sensor_signature,
            "resolution_strategy": resolution_strategy,
            "time_to_recover_mins": time_to_recover_mins
        })


vector_memory = IncidentVectorMemoryEngine()
