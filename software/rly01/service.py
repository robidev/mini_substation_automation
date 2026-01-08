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

SERIAL_DEV = "/dev/ttyAMA5"
BAUD = 115200
NUM_CHANNELS = 10

# ---------------- Shared State ----------------

tx_queue = Queue()         # (msg, client_conn) for command-response
shutdown = threading.Event()

event = [None for _ in range(NUM_CHANNELS)]  # event[channel] = state
event_lock = threading.Lock()

data_message = ""
data_lock = threading.Lock()

# ---------------- Serial Thread ----------------

def serial_thread():
    """Handles serial I/O to/from slave Pi"""
    ser = serial.Serial(SERIAL_DEV, BAUD, timeout=0.1)

    def write_loop():
        while not shutdown.is_set():
            msg, client = tx_queue.get()
            ser.write((msg + "\n").encode())
            # ACK back to client immediately (optional)
            client.sendall(b"OK\n")

    threading.Thread(target=write_loop, daemon=True).start()

    while not shutdown.is_set():
        line = ser.readline()
        if not line:
            continue
        msg = line.decode(errors="ignore").strip()

        # Parse events or data messages
        # Example slave messages:
        # "SERVO 3 START 120"
        # "SERVO 3 END 120"
        # "DATA xyz"

        parts = msg.split()
        if not parts:
            continue

        if parts[0] == "SERVO" and len(parts) >= 4:
            try:
                ch = int(parts[1])
                state = parts[2] + "_" + parts[3]  # e.g., "START_120" or "END_120"
                with event_lock:
                    if 0 <= ch < NUM_CHANNELS:
                        event[ch] = state
            except:
                continue
        elif parts[0] == "DATA":
            with data_lock:
                data_message = " ".join(parts[1:])

# ---------------- Unix Socket Client Handler ----------------

def handle_client(conn, addr):
    """Each Unix socket connection runs here"""
    with conn:
        while not shutdown.is_set():
            try:
                data = conn.recv(1024)
                if not data:
                    break
                cmd = data.decode(errors="ignore").strip().split()

                if not cmd:
                    continue

                if cmd[0] == "SET" and len(cmd) == 3:
                    ch = int(cmd[1])
                    state_val = cmd[2]
                    tx_queue.put((f"SET {ch} {state_val}", conn))

                elif cmd[0] == "GETEVENT" and len(cmd) == 2:
                    ch = int(cmd[1])
                    with event_lock:
                        state_val = event[ch] if 0 <= ch < NUM_CHANNELS else "UNKNOWN"
                    conn.sendall((str(state_val) + "\n").encode())

                elif cmd[0] == "GETDATA":
                    with data_lock:
                        msg = data_message
                    conn.sendall((msg + "\n").encode())

                else:
                    conn.sendall(b"ERR UNKNOWN_CMD\n")

            except Exception as e:
                print(f"Client error {addr}: {e}")
                break

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
            print(f"Unix socket error {path}: {e}")
            continue

# ---------------- Main ----------------

def main():
    # Start serial thread
    threading.Thread(target=serial_thread, daemon=True).start()

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
