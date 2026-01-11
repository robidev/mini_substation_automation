import socket
import sys
import threading
import time

shutdown = threading.Event()

def receiver_thread(client):
    """Continuously receives and displays messages from the server"""
    buffer = ""
    
    while not shutdown.is_set():
        try:
            data = client.recv(1024)
            if not data:
                print("\n[Server closed connection]")
                shutdown.set()
                break
            
            # Decode and add to buffer
            buffer += data.decode(errors="ignore")
            
            # Process complete lines
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                
                if not line:
                    continue
                
                # Check if it's a broadcast event
                if line.startswith("EVENT "):
                    parts = line.split(None, 1)
                    if len(parts) > 1:
                        print(f"\n[BROADCAST] {parts[1]}")
                    else:
                        print(f"\n[BROADCAST] {line}")
                    print("> ", end="", flush=True)
                else:
                    # Regular response
                    print(f"\n[RESPONSE] {line}")
                    print("> ", end="", flush=True)
                    
        except socket.timeout:
            continue
        except Exception as e:
            if not shutdown.is_set():
                print(f"\n[Receiver error: {e}]")
            break

def main():
    if len(sys.argv) != 2:
        print("Usage: python unix_socket_test.py <unix_socket_path>")
        sys.exit(1)

    sock_path = sys.argv[1]
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    
    # Set a timeout for recv operations
    client.settimeout(0.5)
    
    try:
        client.connect(sock_path)
    except Exception as e:
        print(f"Failed to connect to {sock_path}: {e}")
        sys.exit(1)

    print(f"Connected to {sock_path}")
    print("\nCommands:")
    print("  SET <channel> <value>    - Set channel state")
    print("  GET <channel>            - Get current event state for channel")
    print("  GETDATA                  - Get current data message")
    print("  quit                     - Exit program")
    print("\nBroadcast events will be displayed automatically as [BROADCAST]")
    print("-" * 60)

    # Start receiver thread
    recv_thread = threading.Thread(target=receiver_thread, args=(client,), daemon=True)
    recv_thread.start()

    try:
        while not shutdown.is_set():
            try:
                cmd = input("> ").strip()
            except EOFError:
                break
                
            if not cmd:
                continue
                
            if cmd.lower() in ("quit", "exit"):
                break

            # Send command
            try:
                client.sendall((cmd + "\n").encode())
            except Exception as e:
                print(f"[Send error: {e}]")
                break

    except KeyboardInterrupt:
        print("\n[Interrupted]")
    finally:
        shutdown.set()
        client.close()
        print("Disconnected")

if __name__ == "__main__":
    main()