"""
AirGuard AI - Multi-Channel Smart Alert Dispatcher (Section 3.3, v2.0)
Implements:
1. Priority-based routing:
   - Critical (AQI > 200 or CO2 > 2000 ppm): Hardware Buzzer + RGB Red Flash + App Push + Twilio SMS
   - Moderate (AQI 100-200 or CO2 1000-2000 ppm): App Push + Web Dashboard Toast + SMTP Email
2. Dispatch channels: WebSockets, Simulated Twilio SMS, Simulated SMTP Email, and Hardware MQTT Commands.
"""

from typing import List, Dict, Any
from datetime import datetime


class AlertDispatcher:
    def __init__(self):
        self.dispatch_log: List[Dict[str, Any]] = []

    def evaluate_priority_and_channels(
        self,
        aqi: int,
        co2: float,
        pm25: float,
        severity: str
    ) -> Dict[str, Any]:
        """
        Evaluates alert priority and determines dispatch channels based on Section 3.3 rules.
        """
        is_critical = (
            aqi > 200 or
            co2 > 2000.0 or
            pm25 > 150.0 or
            severity == "CRITICAL"
        )

        if is_critical:
            priority = "CRITICAL"
            channels = [
                "HARDWARE_BUZZER_RGB",
                "APP_PUSH",
                "SMS_TWILIO",
                "WEB_DASHBOARD_TOAST"
            ]
        else:
            priority = "WARNING"
            channels = [
                "WEB_DASHBOARD_TOAST",
                "APP_PUSH",
                "EMAIL_SMTP"
            ]

        return {
            "priority": priority,
            "channels": channels,
            "channels_str": ",".join(channels)
        }

    async def dispatch(
        self,
        device_id: str,
        title: str,
        message: str,
        recommendation: str,
        priority: str,
        channels: List[str]
    ) -> Dict[str, Any]:
        """
        Dispatches multi-channel alerts across configured delivery mediums.
        """
        results = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": priority,
            "dispatched_channels": channels,
            "delivery_receipts": {}
        }

        # 1. Local Device Hardware (Buzzer + RGB LED Flash)
        if "HARDWARE_BUZZER_RGB" in channels:
            receipt = f"[EDGE_HARDWARE:{device_id}] Buzzer ALARM & RGB Red Flash triggered"
            results["delivery_receipts"]["HARDWARE"] = receipt
            print(f"[AlertDispatcher] {receipt}")

        # 2. Twilio SMS Dispatch
        if "SMS_TWILIO" in channels:
            sms_body = f"[AirGuard AI 🚨 {priority}] {title} in {device_id}: {message} Rec: {recommendation}"
            receipt = f"[TWILIO_SMS -> +1-555-AIR-GUARD] Delivered: '{sms_body[:80]}...'"
            results["delivery_receipts"]["SMS"] = receipt
            print(f"[AlertDispatcher] {receipt}")

        # 3. SMTP Email Dispatch
        if "EMAIL_SMTP" in channels:
            subject = f"AirGuard AI Advisory: {title}"
            receipt = f"[SMTP_EMAIL -> occupant@airguard.ai] Sent subject: '{subject}'"
            results["delivery_receipts"]["EMAIL"] = receipt
            print(f"[AlertDispatcher] {receipt}")

        # 4. App Push Notification
        if "APP_PUSH" in channels:
            results["delivery_receipts"]["APP_PUSH"] = f"APNS/FCM Push token broadcast for device {device_id}"

        # 5. Web Dashboard Toast
        if "WEB_DASHBOARD_TOAST" in channels:
            results["delivery_receipts"]["WEB_TOAST"] = f"Real-time WebSocket toast broadcast"

        self.dispatch_log.append(results)
        return results


alert_dispatcher = AlertDispatcher()
