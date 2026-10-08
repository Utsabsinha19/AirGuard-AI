"""
AirGuard AI - Multi-Room IoT Fleet Simulator Runner (Enhanced)
"""

import time
import argparse
from datetime import datetime, timedelta
from simulator.virtual_device import VirtualEdgeNode


def seed_initial_history(nodes, backend_url="http://127.0.0.1:8000/api", minutes_back=30):
    print(f"[Simulator] Seeding {minutes_back} minutes of realistic historical telemetry...")
    now = datetime.utcnow()
    for m in range(minutes_back, 0, -1):
        ts = now - timedelta(minutes=m)
        for node in nodes:
            node.step_physics()
            payload = {
                "device_id": node.device_id,
                "timestamp": ts.isoformat(),
                "pm2_5": round(node.pm2_5, 1),
                "pm10": round(node.pm10, 1),
                "co2": round(node.co2, 0),
                "voc": round(node.voc, 1),
                "temperature": round(node.temperature, 1),
                "humidity": round(node.humidity, 1),
                "pressure": round(node.pressure, 1),
                "ambient_light": round(node.ambient_light, 1),
                "noise_level": round(node.noise_level, 1),
                "battery_pct": node.battery_pct,
                "latitude": node.latitude,
                "longitude": node.longitude
            }
            try:
                import requests
                requests.post(f"{backend_url}/telemetry/ingest", json=payload, timeout=0.8)
            except Exception:
                pass
    print("[Simulator] Historical seeding complete!")


def run_fleet_simulation(backend_url="http://127.0.0.1:8000/api", seed_history=True, interval_seconds=2.0):
    print("=" * 60)
    print("AirGuard AI - Launching Multi-Room Virtual Sensor Fleet")
    print(f"Target Backend: {backend_url}")
    print(f"Sampling Interval: {interval_seconds}s")
    print("=" * 60)

    nodes = [
        VirtualEdgeNode("AG-001", "Master Bedroom", backend_url, baseline_pm=7.0, baseline_co2=580.0, baseline_voc=85.0, latitude=37.7749, longitude=-122.4194),
        VirtualEdgeNode("AG-002", "Living Room", backend_url, baseline_pm=11.0, baseline_co2=640.0, baseline_voc=110.0, latitude=37.7749, longitude=-122.4192),
        VirtualEdgeNode("AG-003", "Kitchen", backend_url, baseline_pm=14.0, baseline_co2=520.0, baseline_voc=130.0, latitude=37.7748, longitude=-122.4193),
        VirtualEdgeNode("AG-004", "Home Office", backend_url, baseline_pm=8.5, baseline_co2=750.0, baseline_voc=95.0, latitude=37.7750, longitude=-122.4195),
    ]

    if seed_history:
        seed_initial_history(nodes, backend_url, minutes_back=30)

    step = 0
    print("[Simulator] Fleet streaming started. Press Ctrl+C to terminate.")

    try:
        while True:
            step += 1
            if step % 45 == 0:
                print("[Simulator] Injecting minor culinary activity in Kitchen (AG-003)...")
                nodes[2].trigger_event("cooking", duration_steps=10)

            for node in nodes:
                node.transmit()

            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n[Simulator] Simulation paused.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AirGuard AI Virtual Sensor Fleet")
    parser.add_argument("--url", default="http://127.0.0.1:8000/api", help="FastAPI backend endpoint")
    parser.add_argument("--interval", type=float, default=2.0, help="Sampling interval in seconds")
    parser.add_argument("--no-seed", action="store_true", help="Skip historical data seeding")
    args = parser.parse_args()

    run_fleet_simulation(backend_url=args.url, seed_history=not args.no_seed, interval_seconds=args.interval)
