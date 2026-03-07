# Haptic-Q: QSDC-Synchronized Real-Time Feedback System

This project implements a secure, low-latency tele-robotic surgery platform with quantum-secured communication and haptic feedback.

## System Architecture

1.  **Quantum Security Layer (`qsdc_engine.py`)**: Simulates Quantum Secure Direct Communication (QSDC) using entanglement to detect eavesdropping on control signals.
2.  **Tele-Operation Bridge (`teleop_bridge.py`)**: The central hub that routes data between the console, robot, and dashboard. It hosts a TCP server for the console and a WebSocket server for the Web Dashboard.
3.  **Surgeon Console (`surgeon_console.py`)**: The local interface for the surgeon. Captures Joystick input, displays a live OpenCV video feed with HUD overlays, and receives haptic telemetry.
4.  **Feedback Sync (`feedback_sync.py`)**: Logic for low-latency synchronization of FSR (pressure) data to haptic actuators.
5.  **Robot Firmware (`robot_firmware.ino`)**: Arduino code for controlling servos with surgical precision and reading the FSR sensor.
6.  **Web Dashboard (`dashboard/`)**: A "Medical Grade" real-time telemetry display built with Next.js and Recharts.

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Node.js & npm
- Arduino IDE (for firmware)
- Required Python Packages:
  ```bash
  pip install qiskit opencv-python pygame websockets numpy
  ```

### 2. Running the System (Local Simulation)

**Step 1: Start the Tele-Operation Bridge**
```bash
python teleop_bridge.py
```

**Step 2: Start the Surgeon Console**
```bash
python surgeon_console.py
```

**Step 3: Start the Web Dashboard**
```bash
cd dashboard
npm run dev
```
Visit `http://localhost:3000` to see the telemetry.

**Step 4: (Hardware) Upload Firmware**
- Connect your Arduino with servos on Pins 9, 10 and FSR on A0.
- Upload `robot_firmware.ino`.

## Simulation Features
- **Eavesdropping Detection**: The `QSDCEngine` will randomly simulate link integrity drops. If the integrity falls below the threshold, the bridge will trigger a **Lockout**.
- **Visual Alert**: The Surgeon Console and Web Dashboard will flash red when a security breach is detected.
- **HUD Overlay**: Real-time stats for Force Applied and Quantum Link Integrity are shown directly on the video feed.
