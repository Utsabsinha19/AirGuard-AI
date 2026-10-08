# AirGuard AI — ESP32 Hardware Firmware (FR-1, FR-2)

This directory contains the production-grade C/C++ firmware for the **AirGuard AI** IoT Edge Node, running on the Espressif ESP32 dual-core microcontroller.

---

## 1. Hardware Bill of Materials (BOM)

| Component | Interface | Description | Pin Mapping (ESP32) |
| :--- | :--- | :--- | :--- |
| **ESP32 DevKit V1** | Microcontroller | Wi-Fi 802.11 b/g/n, BLE, Dual 240MHz Tensilica | — |
| **Plantower PMS5003** | UART (9600 baud) | Laser scattering particulate mass (PM1.0, PM2.5, PM10) | RX -> `GPIO 17 (TX1)`<br>TX -> `GPIO 16 (RX1)` |
| **Winsen MH-Z19B** | UART (9600 baud) | NDIR Carbon Dioxide sensor (400–5000 ppm) | RX -> `GPIO 26 (TX2)`<br>TX -> `GPIO 25 (RX2)` |
| **Sensirion SGP30** | I2C (Address `0x58`)| MOX Volatile Organic Compounds (tVOC, eCO2) | SDA -> `GPIO 21`<br>SCL -> `GPIO 22` |
| **Sensirion SHT31** | I2C (Address `0x44`)| High-precision digital temperature & humidity | SDA -> `GPIO 21`<br>SCL -> `GPIO 22` |
| **SSD1306 0.96" OLED**| I2C (Address `0x3C`)| 128x64 Monochrome graphical display | SDA -> `GPIO 21`<br>SCL -> `GPIO 22` |
| **RGB Status LED** | Digital / PWM | Visual threat color coding (Green / Amber / Red / Purple)| R: `GPIO 12`, G: `GPIO 14`, B: `GPIO 27` |
| **Active Buzzer** | Digital | Audible threat alarm | `GPIO 13` |
| **Battery ADC** | Analog In | 3.7V LiPo voltage divider monitor | `GPIO 34 (ADC1_CH6)` |

---

## 2. Pinout Wiring Schematic

```
               ┌───────────────────────┐
               │      ESP32 DevKit     │
               │                       │
 [PMS5003 TX] ─┤ GPIO 16 (RX1)         │
 [PMS5003 RX] ─┤ GPIO 17 (TX1)         │
 [MH-Z19B TX] ─┤ GPIO 25 (RX2)         │
 [MH-Z19B RX] ─┤ GPIO 26 (TX2)         │
               │                       │
  [I2C SDA]   ─┤ GPIO 21 (SDA)         │──► SHT31, SGP30, SSD1306 OLED
  [I2C SCL]   ─┤ GPIO 22 (SCL)         │──► SHT31, SGP30, SSD1306 OLED
               │                       │
  [RGB Red]   ─┤ GPIO 12               │──► Red Anode
  [RGB Green] ─┤ GPIO 14               │──► Green Anode
  [RGB Blue]  ─┤ GPIO 27               │──► Blue Anode
  [Buzzer]    ─┤ GPIO 13               │──► Buzzer Positive (+)
               │                       │
  [3.3V / 5V] ─┤ 3V3 / VIN             │──► Sensor VCC
  [GND]       ─┤ GND                   │──► Common Ground
               └───────────────────────┘
```

---

## 3. Features & Operating Modes

- **Sub-Second Telemetry Pipeline:** Samples environmental readings every 2000 ms and transmits structured JSON telemetry to MQTT topic `airguard/{device_id}/telemetry`.
- **Resilient Offline Queuing (FR-2.3, NFR-2):** If Wi-Fi or MQTT disconnects, incoming readings are enqueued to an internal circular FIFO buffer. When network connectivity is restored, all buffered readings are sequentially drained to the cloud broker without dropping packets.
- **Embedded Visual Feedback (FR-1.3):** Displays live numeric metrics on the 128x64 OLED screen, adjusts RGB LED color based on AQI tier, and sounds acoustic alarm pulses during hazardous spikes.

---

## 4. How to Compile & Flash

1. Install [PlatformIO](https://platformio.org/) in VS Code or CLI.
2. Edit `src/config.h` to set your local Wi-Fi SSID and MQTT Broker IP.
3. Connect your ESP32 board via USB.
4. Run:
```bash
# Compile firmware
pio run

# Upload to ESP32
pio run --target upload

# Open Serial Monitor (115200 baud)
pio device monitor
```
