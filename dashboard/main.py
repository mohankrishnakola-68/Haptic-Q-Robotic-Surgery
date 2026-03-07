from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import random
import time

app = FastAPI(title="Haptic-Q Tele-Operation Dashboard")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Haptic-Q | Surgeon Command Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0e14;
            --panel: #151a24;
            --accent: #00ffd4;
            --danger: #ff3c41;
            --text: #e0e6f0;
            --text-dim: #8c96a5;
            --glow: rgba(0, 255, 212, 0.4);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Outfit', sans-serif;
            overflow: hidden;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(20, 30, 50, 0.5) 0%, transparent 100%),
                linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
        }

        .header {
            height: 80px;
            background: rgba(21, 26, 36, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 3px solid var(--accent);
            display: flex;
            align-items: center;
            padding: 0 40px;
            justify-content: space-between;
            box-shadow: 0 0 30px rgba(0, 255, 212, 0.15);
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: 2px;
            color: var(--text);
        }
        .logo span { color: var(--accent); text-shadow: 0 0 10px var(--glow); }

        .status-badge {
            background: rgba(0, 255, 212, 0.1);
            border: 1px solid var(--accent);
            color: var(--accent);
            padding: 8px 20px;
            border-radius: 4px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 0.8; box-shadow: 0 0 5px var(--glow); }
            50% { opacity: 1; box-shadow: 0 0 15px var(--glow); }
            100% { opacity: 0.8; box-shadow: 0 0 5px var(--glow); }
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 30px;
            padding: 30px;
            height: calc(100vh - 80px);
        }

        .video-feed {
            background: var(--panel);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .video-feed::before {
            content: "SECURE LIVE STREAMING";
            position: absolute;
            top: 20px;
            left: 20px;
            font-family: 'JetBrains Mono';
            font-size: 0.8rem;
            color: var(--accent);
            opacity: 0.7;
        }

        .scanline {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(to bottom, transparent 50%, rgba(0, 255, 212, 0.02) 50.5%, transparent 51%);
            background-size: 100% 4px;
            pointer-events: none;
            z-index: 10;
        }

        .telemetry-column {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .card {
            background: var(--panel);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 24px;
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); border-color: rgba(0, 255, 212, 0.3); }

        .card-title {
            color: var(--text-dim);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
        }

        .value-display {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent);
            font-family: 'JetBrains Mono', monospace;
        }
        .value-display span { font-size: 1rem; color: var(--text-dim); margin-left: 5px; }

        .graph-container {
            margin-top: 20px;
            height: 80px;
            display: flex;
            align-items: flex-end;
            gap: 3px;
        }

        .graph-bar {
            flex: 1;
            background: var(--accent);
            opacity: 0.3;
            border-radius: 2px;
            transition: height 0.5s ease;
        }

        .system-controls {
            margin-top: auto;
            background: rgba(255, 60, 65, 0.05);
            border: 1px solid rgba(255, 60, 65, 0.2);
        }
        .system-controls .card-title { color: var(--danger); }
        .system-controls .value-display { color: var(--danger); text-shadow: none; }

        button {
            width: 100%;
            padding: 15px;
            margin-top: 20px;
            background: var(--danger);
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 700;
            cursor: pointer;
            text-transform: uppercase;
            transition: 0.3s;
        }
        button:hover { background: #ff5257; }

        /* Tech Hud Corners */
        .corner {
            position: absolute;
            width: 30px;
            height: 30px;
            border-color: var(--accent);
            border-style: solid;
        }
        .top-left { top: 15px; left: 15px; border-width: 3px 0 0 3px; }
        .top-right { top: 15px; right: 15px; border-width: 3px 3px 0 0; }
        .bottom-left { bottom: 15px; left: 15px; border-width: 0 0 3px 3px; }
        .bottom-right { bottom: 15px; right: 15px; border-width: 0 3px 3px 0; }

        .placeholder-vid {
            text-align: center;
            opacity: 0.5;
        }
        .placeholder-vid svg { width: 80px; color: var(--accent); margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">HAPTIC-<span>Q</span></div>
        <div class="status-badge" id="main-status">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: var(--accent);"></span>
            QUANTUM SECURE LINK ACTIVE
        </div>
    </div>

    <div class="main-grid">
        <div class="video-feed">
            <div class="corner top-left"></div>
            <div class="corner top-right"></div>
            <div class="corner bottom-left"></div>
            <div class="corner bottom-right"></div>
            <div class="scanline"></div>
            
            <div class="placeholder-vid">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M23 7l-7 5 7 5V7z" />
                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
                </svg>
                <p>TELE-PRESENCE VIDEO STREAM ACTIVE</p>
                <small style="color: var(--accent); display: block; margin-top: 10px; font-family: 'JetBrains Mono';">AES-QST ENCRYPTED</small>
            </div>
        </div>

        <div class="telemetry-column">
            <div class="card">
                <div class="card-title">Haptic Force <span>REF: 255 mN</span></div>
                <div class="value-display" id="force-val">142<span>mN</span></div>
                <div class="graph-container">
                    <div class="graph-bar" style="height: 40%"></div>
                    <div class="graph-bar" style="height: 60%"></div>
                    <div class="graph-bar" style="height: 55%"></div>
                    <div class="graph-bar" style="height: 70%"></div>
                    <div class="graph-bar" style="height: 65%"></div>
                    <div class="graph-bar" style="height: 85%"></div>
                    <div class="graph-bar" style="height: 50%"></div>
                    <div class="graph-bar" style="height: 60%"></div>
                    <div class="graph-bar" style="height: 75%"></div>
                    <div class="graph-bar" style="height: 80%"></div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">Quantum Integrity <span>OPT: 100%</span></div>
                <div class="value-display" id="integrity-val">99.8<span>%</span></div>
                <div class="graph-container">
                    <div class="graph-bar" style="height: 98%; opacity: 0.5;"></div>
                    <div class="graph-bar" style="height: 99%; opacity: 0.5;"></div>
                    <div class="graph-bar" style="height: 100%; opacity: 0.5;"></div>
                    <div class="graph-bar" style="height: 98%; opacity: 0.5;"></div>
                    <div class="graph-bar" style="height: 99%; opacity: 0.5;"></div>
                    <div class="graph-bar" style="height: 97%; opacity: 0.5;"></div>
                    <div class="graph-bar" style="height: 99%; opacity: 0.5;"></div>
                    <div class="graph-bar" style="height: 98%; opacity: 0.5;"></div>
                    <div class="graph-bar" style="height: 100%; opacity: 0.5;"></div>
                    <div class="graph-bar" style="height: 99%; opacity: 0.5;"></div>
                </div>
            </div>

            <div class="card system-controls">
                <div class="card-title">System Status</div>
                <div class="value-display" id="sec-msg">NORMAL</div>
                <button onclick="emergencyStop()">EMERGENCY DISCONNECT</button>
            </div>
        </div>
    </div>

    <script>
        function updateTelemetry() {
            // Simulated real-time updates
            const force = Math.floor(Math.random() * 40 + 120);
            const integrity = (99 + Math.random()).toFixed(1);
            
            document.getElementById('force-val').innerHTML = `${force}<span>mN</span>`;
            document.getElementById('integrity-val').innerHTML = `${integrity}<span>%</span>`;
            
            // Shift bars
            const bars = document.querySelectorAll('.graph-bar');
            bars.forEach(bar => {
                const h = Math.random() * 60 + 20;
                bar.style.height = h + '%';
            });
        }

        function emergencyStop() {
            alert('EMERGENCY DISCONNECT SEQUENCE INITIATED');
            document.getElementById('main-status').style.backgroundColor = 'var(--danger)';
            document.getElementById('main-status').style.borderColor = 'var(--danger)';
            document.getElementById('main-status').innerHTML = 'SYSTEM LOCKDOWN - BREACH DETECTED';
            document.body.style.boxShadow = 'inset 0 0 200px rgba(255, 60, 65, 0.4)';
        }

        setInterval(updateTelemetry, 1000);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
