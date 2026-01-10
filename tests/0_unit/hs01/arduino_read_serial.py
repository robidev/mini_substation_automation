import serial
import time

def crc8(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc



ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.2)

def request_adc_frames(n):
    cmd = f"@ADC:{n}\n".encode()
    ser.write(cmd)

ADC_NUM_CHANNELS = 12
ADC_WIRE_COUNT = 6

def read_adc_packet():
    # Sync on header 0xAA 0x55
    while True:
        b = ser.read(1)
        if not b:
            return None
        if b == b'\xAA':
            if ser.read(1) == b'\x55':
                break

    length = ser.read(1)
    if not length:
        return None

    payload_len = length[0]
    payload = ser.read(payload_len)
    crc_rx = ser.read(1)
    tail = ser.read(2)

    if len(payload) != payload_len or len(crc_rx) != 1:
        return None

    if tail != b'\r\n':
        print("Invalid packet tail")
        return None

    crc_calc = crc8(length + payload)
    if crc_calc != crc_rx[0]:
        print("CRC error")
        return None

    # Decode ADCs
    adc = []
    idx = 0
    for _ in range(ADC_NUM_CHANNELS):
        val = payload[idx] | (payload[idx + 1] << 8)
        adc.append(val)
        idx += 2

    # Decode short matrix (bitmasks)
    short_matrix = payload[idx:idx + ADC_WIRE_COUNT]

    return adc, short_matrix

def print_packet(adc, short_matrix):
    print("ADC values:")
    for i, v in enumerate(adc):
        print(f"  CH{i:02d}: {v}")

    print("\nShort matrix:")
    for i, mask in enumerate(short_matrix):
        shorts = [j for j in range(ADC_WIRE_COUNT) if mask & (1 << j)]
        print(f"  Wire {i}: shorts with {shorts}")


# WARNING: this program will reset the arduino on start due to kernel USB-driver pulling DTR low, which resets the arduino
time.sleep(4) # settle time after reset
print("STARTED!")
request_adc_frames(10)

while True:
    pkt = read_adc_packet()
    if not pkt:
        continue

    adc, shorts = pkt
    print_packet(adc, shorts)
    print("-" * 40)

