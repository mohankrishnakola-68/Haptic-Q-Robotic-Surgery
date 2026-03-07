import socket
import threading
import json
import time
import asyncio
import websockets
from qsdc_engine import QSDCEngine

class TeleopBridge:
    """
    Acts as the secure communication hub between the Surgeon Console and the Robotic Arm.
    Integrates the QSDC Engine for real-time security monitoring.
    Broadcasts telemetry to a Web Dashboard via WebSockets.
    """
    def __init__(self, host='127.0.0.1', port=5555, ws_port=5556):
        self.host = host
        self.port = port
        self.ws_port = ws_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.qsdc = QSDCEngine()
        self.console_conn = None
        
        self.ws_clients = set()
        self.loop = None
        
        self.running = True
        self.force_value = 0
        print(f"[*] Teleop Bridge started on {host}:{port}")
        print(f"[*] WebSocket Server ready on ws://{host}:{ws_port}")

    async def ws_handler(self, websocket, path):
        self.ws_clients.add(websocket)
        try:
            async for message in websocket:
                pass # We only broadcast to dashboard
        finally:
            self.ws_clients.remove(websocket)

    async def start_ws_server_async(self):
        self.loop = asyncio.get_running_loop()
        async with websockets.serve(self.ws_handler, self.host, self.ws_port):
            await asyncio.Future()  # run forever

    def start_ws_server(self):
        asyncio.run(self.start_ws_server_async())

    def handle_console(self, conn):
        self.console_conn = conn
        print("[+] Surgeon Console Connected.")
        while self.running:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                # Check link integrity before forwarding
                if not self.qsdc.check_integrity():
                    pass
                
                # Simulate receiving robot pressure data
                self.force_value = np.random.randint(0, 1024) if not self.qsdc.lockout_active else 0
                
            except Exception:
                break
        print("[-] Console disconnected.")

    def broadcast_status(self):
        """Sends QSDC status to the connected dashboard/console."""
        status = self.qsdc.get_status()
        packet = {
            "type": "telemetry", 
            "data": {
                **status,
                "force": self.force_value,
                "timestamp": time.time()
            }
        }
        json_packet = json.dumps(packet)
        
        # Send to TCP console
        if self.console_conn:
            try:
                self.console_conn.send(json_packet.encode())
            except:
                pass
        
        # Send to Web Dashboard
        if self.ws_clients and self.loop:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_ws(json_packet), self.loop
                )
            except Exception as e:
                print(f"[!] WS Broadcast Error: {e}")

    async def broadcast_ws(self, packet):
        if self.ws_clients:
            # Create tasks for all clients
            websockets_list = list(self.ws_clients)
            for ws in websockets_list:
                try:
                    await ws.send(packet)
                except:
                    self.ws_clients.remove(ws)

    def run(self):
        # Start WebSocket server in a separate thread
        threading.Thread(target=self.start_ws_server, daemon=True).start()
        
        # Start a background thread for periodic integrity checks
        threading.Thread(target=self.integrity_monitor, daemon=True).start()
        
        while self.running:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_console, args=(conn,)).start()

    def integrity_monitor(self):
        while self.running:
            self.broadcast_status()
            time.sleep(0.5)

if __name__ == "__main__":
    import numpy as np
    bridge = TeleopBridge()
    bridge.run()
