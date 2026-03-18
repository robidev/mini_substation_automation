from pymodbus.client.sync import ModbusTcpClient

# Server IP and port
SERVER_IP = "172.16.1.12"
SERVER_PORT = 502

# List of Unit IDs to poll
unit_ids = [1, 2, 3, 4, 5, 6, 7, 8]

# Example register to read (holding register address)
REGISTER_ADDR = 0   # first register
REGISTER_COUNT = 1  # number of registers to read

def main():
    # Connect once to the server
    client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)
    if not client.connect():
        print("Failed to connect to server")
        return

    print(f"Connected to {SERVER_IP}:{SERVER_PORT}")

    for unit in unit_ids:
        # Read holding registers from this unit ID
        response = client.read_holding_registers(
            address=REGISTER_ADDR,
            count=REGISTER_COUNT,
            unit=unit
        )

        if response.isError():
            print(f"Unit ID {unit}: Error - {response}")
        else:
            print(f"Unit ID {unit}: Registers = {response.registers}")

    client.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()

