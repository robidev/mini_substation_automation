"""
IEC61850 client for communication with relay servers
"""
import socket
import json
import threading
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from config import ELEMENTS


@dataclass
class RelayData:
    """Data structure for relay measurements and status"""
    name: str
    connected: bool = False
    # Dynamic element storage for flexible element access
    elements: Dict[str, Any] = field(default_factory=dict)
    
    def set_element_value(self, element_name: str, value: Any):
        """Set the value for a named element"""
        self.elements[element_name] = value
    
    def get_element_value(self, element_name: str, default: Any = None) -> Any:
        """Get the value for a named element"""
        return self.elements.get(element_name, default)


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
            #print(f"Failed to connect to {self.socket_path}: {e}")
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
                    print("response: " + str(response))
                    with self.lock:
                        # Populate elements from response data
                        for element_name in ELEMENTS[self.relay_id]:
                            element_cfg = ELEMENTS[self.relay_id][element_name]
                            element_type = element_cfg.get("type")
                            
                            if element_type in ("breaker", "switch"):
                                # Get state for breaker/switch (e.g., cbr1, swi1)
                                state = response.get(f"{element_name}", "UNKNOWN")
                                self.data.set_element_value(element_name, state)
                            
                            elif element_type == "measurement":
                                # Get measurement data (e.g., ctr1_data, vtr1_data)
                                data = response.get(f"{element_name}", {})
                                self.data.set_element_value(element_name, data)
                            
                            elif element_type == "setting":
                                # Get setting value directly by element name
                                value = response.get(element_name)
                                if value is not None:
                                    self.data.set_element_value(element_name, value)

                            elif element_type == "status":
                                # Get setting value directly by element name
                                value = response.get(element_name)
                                if value is not None:
                                    self.data.set_element_value(element_name, value)
            
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

    def get_element_value(self, element_name: str, default: Any = None) -> Any:
        """
        Get the value of a named element from config.ELEMENTS
        Args:
            element_name: Name of element (e.g., 'cbr1', 'swi1', 'ctr1')
            default: Default value if element not found
        Returns:
            Element value or default
        """
        with self.lock:
            return self.data.get_element_value(element_name, default)
    
    def get_switch_state(self, element_name: str) -> str:
        """
        Get the state of a breaker or switch element
        Args:
            element_name: Name of breaker/switch element (e.g., 'cbr1', 'swi1')
        Returns:
            State string ("OPEN", "CLOSED", "UNKNOWN", or "INTERMEDIATE")
        """
        if element_name not in ELEMENTS[self.relay_id]:
            return "UNKNOWN"
        
        element_cfg = ELEMENTS[self.relay_id][element_name]
        if element_cfg.get("type") not in ("breaker", "switch"):
            return "UNKNOWN"
        
        with self.lock:
            return self.data.get_element_value(element_name, "UNKNOWN")
    
    def get_measurement(self, element_name: str) -> Optional[Dict]:
        """
        Get measurement data for a transformer element
        Args:
            element_name: Name of measurement element (e.g., 'ctr1', 'vtr1', 'vtr2')
        Returns:
            Dictionary with measurement data or None
        """
        if element_name not in ELEMENTS[self.relay_id]:
            return None
        
        element_cfg = ELEMENTS[self.relay_id][element_name]
        if element_cfg.get("type") != "measurement":
            return None
        
        with self.lock:
            return self.data.get_element_value(element_name, {})
    
    def get_setting(self, element_name: str) -> Any:
        """
        Get a setting value
        Args:
            element_name: Name of setting element (e.g., 'set0_loc', 'set1_Ilarge')
        Returns:
            Setting value or None
        """
        if element_name not in ELEMENTS[self.relay_id]:
            return None
        
        element_cfg = ELEMENTS[self.relay_id][element_name]
        if element_cfg.get("type") != "setting":
            return None
        
        with self.lock:
            return self.data.get_element_value(element_name)
    
    def set_visible(self, visible: bool):
        """Set visibility flag for data updates"""
        self.visible = visible

    def stop(self):
        """Stop the client"""
        self.running = False
        self.disconnect()
