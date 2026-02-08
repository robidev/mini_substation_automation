"""
IEC61850 client for communication with relay servers
"""
import socket
import json
import threading
import time
from typing import Optional, Dict

from models import RelayData, BreakerState


class IEC61850Client:
    """Handles communication with IEC61850 server via Unix socket"""
    
    def __init__(self, socket_path: str, relay_id: int):
        self.socket_path = socket_path
        self.relay_id = relay_id
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.data = RelayData(name=f"Relay {relay_id + 1}")
        self.lock = threading.Lock()
        self.visible = False
        self.running = True
        
    def connect(self):
        """Attempt to connect to the Unix socket"""
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(2.0)
            self.sock.connect(self.socket_path)
            self.connected = True
            self.data.connected = True
            print(f"Connected to {self.socket_path}")
        except Exception as e:
            print(f"Failed to connect to {self.socket_path}: {e}")
            self.connected = False
            self.data.connected = False
            self.sock = None
    
    def disconnect(self):
        """Close the socket connection"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.connected = False
        self.data.connected = False
    
    def send_command(self, command: str, params: Dict = None) -> bool:
        """Send a command to the IEC61850 server"""
        if not self.connected or not self.sock:
            return False
        
        try:
            message = {"command": command}
            if params:
                message.update(params)
            
            data = json.dumps(message) + "\n"
            self.sock.sendall(data.encode())
            return True
        except Exception as e:
            print(f"Error sending command to {self.socket_path}: {e}")
            self.disconnect()
            return False
    
    def receive_data(self) -> Optional[Dict]:
        """Receive data from the IEC61850 server"""
        if not self.connected or not self.sock:
            return None
        
        try:
            # Receive data (assuming newline-delimited JSON)
            buffer = b""
            while b"\n" not in buffer:
                chunk = self.sock.recv(1024)
                if not chunk:
                    raise ConnectionError("Connection closed")
                buffer += chunk
            
            data = buffer.split(b"\n")[0]
            return json.loads(data.decode())
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Error receiving data from {self.socket_path}: {e}")
            self.disconnect()
            return None
    
    def update_loop(self):
        """Background thread to continuously update data"""
        while self.running:
            if not self.connected:
                self.connect()
                time.sleep(2)
                continue
            
            # Request data update
            if self.visible and self.send_command("get_measurements"):
                response = self.receive_data()
                if response:
                    with self.lock:
                        self.data.voltage_l1 = response.get("voltage_l1", 0.0)
                        self.data.voltage_l2 = response.get("voltage_l2", 0.0)
                        self.data.voltage_l3 = response.get("voltage_l3", 0.0)
                        self.data.current_l1 = response.get("current_l1", 0.0)
                        self.data.current_l2 = response.get("current_l2", 0.0)
                        self.data.current_l3 = response.get("current_l3", 0.0)
                        
                        state_str = response.get("breaker_state", "UNKNOWN")
                        try:
                            self.data.breaker_state = BreakerState[state_str]
                        except KeyError:
                            self.data.breaker_state = BreakerState.UNKNOWN
                        
                        # Update IEC61850 specific data
                        self.data.cbr1_state = response.get("cbr1_state", "UNKNOWN")
                        self.data.swi1_state = response.get("swi1_state", "UNKNOWN")
                        self.data.swi2_state = response.get("swi2_state", "UNKNOWN")
                        self.data.swi3_state = response.get("swi3_state", "UNKNOWN")
                        
                        self.data.ctr1_data = response.get("ctr1_data", {})
                        self.data.vtr1_data = response.get("vtr1_data", {})
                        self.data.vtr2_data = response.get("vtr2_data", {})
                        
                        self.data.set0_loc = response.get("set0_loc", "UNKNOWN")
                        self.data.set1_Ilarge = response.get("set1_Ilarge", 0.0)
                        self.data.set2_Tm = response.get("set2_Tm", 0.0)
            
            time.sleep(0.5)  # Update every 500ms
    
    def open_switch(self, element: str) -> bool:
        """Send command to open switch"""
        return self.send_command("open_switch", {"switch": element})
    
    def close_switch(self, element: str) -> bool:
        """Send command to close switch"""
        return self.send_command("close_switch", {"switch": element})

    def write_setting(self, element: str, value: str) -> bool:
        """Send command to alter setting"""
        return self.send_command("write_setting", {"element": element, "value": str(value)})
    
    def get_data(self) -> RelayData:
        """Get the current relay data (thread-safe)"""
        with self.lock:
            return RelayData(**self.data.__dict__)
    
    def set_visible(self, visible: bool):
        """Set visibility flag for data updates"""
        self.visible = visible

    def stop(self):
        """Stop the client"""
        self.running = False
        self.disconnect()
