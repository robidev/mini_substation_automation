#!/bin/env python3
import os
import socket
import threading
from queue import Queue
import serial
import time

# ---------------- Configuration ----------------

UNIX_SOCKETS = [
    "/tmp/api_sock1",
    "/tmp/api_sock2",
    "/tmp/api_sock3",
    "/tmp/api_sock4",
    "/tmp/api_sock5",
    "/tmp/api_sock6",
]

#SERIAL_DEV = "/dev/ttyAMA5"
SERIAL_DEV = "/tmp/ttyV0"
BAUD = 115200
NUM_CHANNELS = 14

# ---------------- Shared State ----------------

tx_queue = Queue()         # Messages to send to serial
shutdown = threading.Event()

event = [None for _ in range(NUM_CHANNELS)]  # event[channel] = state
event_lock = threading.Lock()

data_message = ""
data_lock = threading.Lock()

# Track all connected clients for broadcasting
clients = []
clients_lock = threading.Lock()

# ---------------- Simulated readings ----------------

def analog_data_simulator(data_string):
    """
    Parse sensor data string containing analog and digital measurements.
    
    Args:
        data_string: String in format "A0,1,2,3,4,5,6,7,8,9,10,11 S01,02,03,04,05,06"
  
    Returns:
        dict: Contains 'analog' list of CT and VT values, first 6x input CT, then 6x outgoing CT, then 6x busbar VT
    """
    # Split the string into analog and digital parts
    parts = data_string.strip().split(' ')
    
    # Parse analog values (after 'A')
    analog_part = parts[0][1:]  # Remove 'A' prefix
    analog_values = [int(x) for x in analog_part.split(',')]
    
    # Parse digital hex values (after 'S')
    digital_part = parts[1][1:]  # Remove 'S' prefix
    hex_values = digital_part.split(',')
    
    # Convert hex values to 6x6 boolean matrix
    digital_matrix = []
    for hex_val in hex_values:
        # Convert hex to integer
        value = int(hex_val, 16)
        # Extract first 6 bits (from MSB)
        row = []
        for bit_pos in range(5, -1, -1):  # bits 5 down to 0
            row.append(bool(value & (1 << bit_pos)))
        digital_matrix.append(row)
    

    incoming_ct = analog_values[0:6]
    outgoing_ct = analog_values[6:12]
    busbar_vt = [0] * 6

    ctmap1 = 10
    dismap1 = [2,2,2,3,3,3]
    ctmap2 = 11
    dismap2 = [4,4,4,5,5,5]
    # take over Analog measurements if switches conduct (CT and DIS from feeder)
    for i in range(6): # calculate VT values
        busbar_vt[i] = 0
        if event[ctmap1] == '10' and event[dismap1[i]] == '10':
            busbar_vt[i] = int(incoming_ct[i % 3])
        if event[ctmap2] == '10' and event[dismap2[i]] == '10':
            busbar_vt[i] = int(incoming_ct[(i % 3) + 3 ])
    
    # check if busbar is feeding back TODO: feedback also via feeders 1 and 2 possible!!!
    dismap3 = [6,6,6,7,7,7]
    dismap4 = [8,8,8,9,9,9]
    for i in range(6): # calculate VT values from other busbar, if connected, and voltage is 0
        if event[dismap3[i]] == '10' and event[dismap4[i]] == '10' and busbar_vt[i] > 0:
            if i < 3:
                busbar_vt[i + 3] = busbar_vt[i]
            else:
                busbar_vt[i - 3] = busbar_vt[i]

    # check for short to ground
    # ADC_GND_THRESHOLD = 600;  // ~2.9V (tweak for noise)
    # ADC_SHORT_THRESHOLD = 750; // ~3.6V (tweak for noise)
    short_to_gnd_threshold = 750
    short_to_gnd_current = 50
    gnd_short_active = [False] * 6
    for i, analog_val in enumerate(incoming_ct):
        if analog_val < short_to_gnd_threshold:
            incoming_ct[i] = int(incoming_ct[i] * short_to_gnd_current)
            outgoing_ct[i] = int(outgoing_ct[i] / short_to_gnd_current)
            gnd_short_active[i] = True

    # Process analog values above threshold, and then, if short is detected, increase current for input to simulate a short, and decrease current to outgoing ct's
    # do not process if gnd-fault is already active, we cannot detect both reliably
    threshold = 100
    short_phase_current = 100
    for i, analog_val in enumerate(incoming_ct):
        if analog_val > threshold and gnd_short_active[i] == False:
            # Placeholder for further processing
            if any(digital_matrix[i]):
                incoming_ct[i] = int(incoming_ct[i] * short_phase_current)
                outgoing_ct[i] = int(outgoing_ct[i] / short_phase_current)

    combined = incoming_ct + outgoing_ct + busbar_vt
    output_string = ','.join(map(str, combined))
    return "A" + output_string #simulated_values



# ---------------- Client Broadcasting ----------------

def broadcast_to_clients(message):
    """Send a message to all connected clients"""
    with clients_lock:
        dead_clients = []
        for conn in clients:
            try:
                conn.sendall((message + "\n").encode())
            except Exception as e:
                print(f"Failed to send to client: {e}")
                dead_clients.append(conn)
        
        # Remove dead connections
        for conn in dead_clients:
            clients.remove(conn)
            try:
                conn.close()
            except:
                pass

def register_client(conn):
    """Add a client to the broadcast list"""
    with clients_lock:
        clients.append(conn)
        print(f"Client registered. Total clients: {len(clients)}")

def unregister_client(conn):
    """Remove a client from the broadcast list"""
    with clients_lock:
        if conn in clients:
            clients.remove(conn)
            print(f"Client unregistered. Total clients: {len(clients)}")

# ---------------- Serial Thread ----------------

def serial_thread():
    global data_message
    """Handles serial I/O to/from slave Pi"""
    ser = serial.Serial(SERIAL_DEV, BAUD, timeout=0.1)

    def write_loop():
        while not shutdown.is_set():
            msg = tx_queue.get()
            print(f"msg: {msg}")
            if msg:
                ser.write((msg + "\n").encode())

    threading.Thread(target=write_loop, daemon=True).start()

    while not shutdown.is_set():
        line = ser.readline()
        if not line:
            continue
        msg = line.decode(errors="ignore").strip()

        parts = msg.split()
        if not parts:
            continue

        if parts[0] == "IO" and len(parts) >= 4:
            try:
                mtype = parts[1]
                ch = int(parts[2])
                state = parts[3]
                with event_lock:
                    if 0 <= ch < NUM_CHANNELS:
                        event[ch] = state
                        print(f"IO: {ch} {state}")
                
                if mtype == "B":
                    # Broadcast IO event to all clients
                    broadcast_to_clients(f"EVENT IO {ch} {state}")
            except Exception as e:
                print(f"Except IO: {e}")
                continue
                
        elif parts[0] == "DATA" and len(parts) >= 3:
            mtype = parts[1]
            with data_lock:
                data_message = " ".join(parts[2:])
                print(f"DATA: {data_message}")
            if mtype == "B":
                simulated = analog_data_simulator(data_message)
                # Broadcast DATA event to all clients
                broadcast_to_clients(f"EVENT DATA {simulated}")

# ---------------- Unix Socket Client Handler ----------------

def handle_client(conn, addr):
    """Each Unix socket connection runs here"""
    register_client(conn)
    client_init = False
    
    try:
        with conn:
            while not shutdown.is_set():
                if client_init == False: # ensure, after we connect, we send our current state
                    with event_lock:
                        for ch in range(NUM_CHANNELS):
                            state_t = event[ch]
                            conn.sendall((f"EVENT IO: {ch} {state_t}\n").encode())
                    client_init = True
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    cmd = data.decode(errors="ignore").strip().split()

                    if not cmd:
                        continue

                    if cmd[0] == "SET" and len(cmd) == 3:
                        print(f"SET! {cmd}")
                        ch = int(cmd[1])
                        state_val = cmd[2]
                        tx_queue.put(f"SET {ch} {state_val}")
                        conn.sendall(b"OK\n")

                    elif cmd[0] == "GET" and len(cmd) == 2:
                        ch = int(cmd[1])
                        tx_queue.put(f"GET IO {ch}")
                        with event_lock:
                            state_val = event[ch] if 0 <= ch < NUM_CHANNELS else "UNKNOWN"
                        conn.sendall((str(state_val) + "\n").encode())

                    elif cmd[0] == "GETDATA":
                        tx_queue.put(f"GET DATA")
                        with data_lock:
                            msg = data_message
                        conn.sendall((msg + "\n").encode())

                    else:
                        print("ERROR: unknown cmd: " + str(cmd))
                        conn.sendall(b"ERR UNKNOWN_CMD\n")

                except Exception as e:
                    print(f"Client error {addr}: {e}")
                    break
    finally:
        unregister_client(conn)

# ---------------- Unix Socket Server ----------------

def start_unix_socket(path):
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(path)
    s.listen()
    print(f"Listening on {path}")

    while not shutdown.is_set():
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            if not shutdown.is_set():
                print(f"Unix socket error {path}: {e}")
            continue

# ---------------- Main ----------------

def main():
    # Start serial thread
    threading.Thread(target=serial_thread, daemon=True).start()

    # Initialize all channel values
    for i in range(NUM_CHANNELS):
        tx_queue.put(f"GET IO {i}")
    tx_queue.put(f"GET DATA")

    # Start 6 UNIX socket servers
    for path in UNIX_SOCKETS:
        threading.Thread(target=start_unix_socket, args=(path,), daemon=True).start()



    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown.set()
        print("Shutting down...")

if __name__ == "__main__":
    main()
