import json
import os
import time
import threading
from queue import Queue
import serial

from adafruit_servokit import ServoKit

import RPi.GPIO as GPIO

# List of GPIO pins
swi_gpio_pins = [27, 18, 5, 6, 12, 13, 16, 19, 20, 21]
cbr_gpio_pins = [24, 22, 23, 25]

"""
SET <channel> <0|1>    -> OK | ERR BUSY
GET SERIAL1            -> DATA <processed>

SERVO <ch> <state>     -> event of position

"""

# ---------------- Configuration ----------------

LIMITS_FILE = "servo_limits.json"
NUM_SERVOS = 10
MOVE_SPEED = 0.03
STEP_DEGREE = 1

SERIAL1_DEV = "/dev/ttyACM0" # USB to arduino, WARNING: opening this device will reset the board! 
SERIAL2_DEV = "/dev/ttyAMA0" # serial to second pi
BAUD1 = 115200
BAUD2 = 115200

RECEIVE_FRAMES = 1
ARDUINO_TIMEOUT = 5.0
ADC_NUM_CHANNELS = 12
ADC_WIRE_COUNT = 6

kit = ServoKit(channels=16)

# ---------------- Load limits ----------------

if not os.path.exists(LIMITS_FILE):
    raise FileNotFoundError(f"{LIMITS_FILE} not found")

with open(LIMITS_FILE, "r") as f:
    servo_limits = json.load(f)

# ---------------- Shared state ----------------

servo_queues = [Queue() for _ in range(NUM_SERVOS)]
gpio_queue   = Queue()
servo_busy   = [threading.Event() for _ in range(NUM_SERVOS)]

servo_event_q = Queue()

serial1_data = None
serial1_lock = threading.Lock()

shutdown = threading.Event()

# ---------------- Callbacks ----------------

def on_switch_start(channel, angle):
    servo_event_q.put(f"SERVO {channel} {state}\n")

def on_switch_end(channel, angle):
    servo_event_q.put(f"SERVO {channel} {state}\n")

# ---------------- Servo logic ----------------

def move_servo_smooth(channel, target_angle):
    servo = kit.servo[channel]
    current = servo.angle or 90
    step = STEP_DEGREE if target_angle > current else -STEP_DEGREE

    for angle in range(int(current), int(target_angle), step):
        servo.angle = angle
        time.sleep(MOVE_SPEED)

    servo.angle = target_angle

def servo_worker(channel):
    q = servo_queues[channel]

    while not shutdown.is_set():
        target,state = q.get()
        servo_busy[channel].set()

        on_switch_start(channel, state)
        move_servo_smooth(channel, target)
        
        GPIO.output(swi_gpio_pins[channel],state) #set pin
        on_switch_end(channel, state)

        servo_busy[channel].clear()

# ---------------- gpio logic ----------------

def gpio_worker():
    q = gpio_queue

    while not shutdown.is_set():
        channel,state = q.get()
        GPIO.output(cbr_gpio_pins[channel + 10],state)

# ---------------- Public API ----------------

def set_switch(channel, state):
    if not (0 <= channel < NUM_SERVOS):
        return "ERR INVALID_CHANNEL\n"

    if servo_busy[channel].is_set():
        return "ERR BUSY\n"

    limits = servo_limits.get(str(channel))
    if not limits:
        return "ERR NO_LIMITS\n"

    target = limits["upper"] if state else limits["lower"]
    if target is None:
        return "ERR BAD_LIMIT\n"
    if channel < 10:
        servo_queues[channel].put((target,state))
    else:
        gpio_queue.put((channel,state))
    return "OK\n"

# ---------------- Serial1 reader ----------------

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


def serial1_writer(ser):
    n = RECEIVE_FRAMES
    while not shutdown.is_set():
        cmd = f"@ADC:{n}\n".encode()
        ser.write(cmd)
        time.sleep(1) # sleep for 1 second

def read_adc_packet(ser):
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

def format_packet_oneline(adc, short_matrix):
    # ADC values: decimal
    adc_part = "A" + ",".join(str(v) for v in adc)
    # Short matrix: 6 bytes as lowercase hex, 2 chars each
    short_part = "S" + ",".join(f"{b:02x}" for b in short_matrix)
    return adc_part + " " + short_part

def serial1_reader(ser):
    global serial1_data
    while not shutdown.is_set():
        pkt = read_adc_packet(ser)
        if not pkt:
            continue

        adc, shorts = pkt
        #print_packet(adc, shorts)
        processed = format_packet_oneline(adc, shorts)
        #print(processed)

        with serial1_lock:
            serial1_data = processed

# ---------------- Serial2 API (slave) ----------------

def serial2_api(ser):
    while not shutdown.is_set():
        line = ser.readline()
        if not line:
            continue

        cmd = line.decode(errors="ignore").strip().split()

        if not cmd:
            continue

        if cmd[0] == "SET" and len(cmd) == 3:
            ch = int(cmd[1])
            state = cmd[2] == "1"
            #ser.write(set_switch(ch, state).encode())
            servo_event_q.put(set_switch(ch, state))

        elif cmd[0] == "GET" and cmd[1] == "SERIAL1":
            with serial1_lock:
                data = serial1_data or ""
            #ser.write(f"DATA {data}\n".encode())
            servo_event_q.put(f"DATA {data}\n")

        else:
            msg= b"ERR UNKNOWN_CMD\n"
            servo_event_q.put(msg)

# ---------------- Event reporter ----------------

def serial2_writer(ser):
    while not shutdown.is_set():
        msg = servo_event_q.get()
        ser.write(msg.encode())


# ---------------- Startup ----------------

def main():
    ser1 = serial.Serial(SERIAL1_DEV, BAUD1, timeout=1)
    ser2 = serial.Serial(SERIAL2_DEV, BAUD2, timeout=1)

    print("sleeping until arduino has been reset")
    time.sleep(ARDUINO_TIMEOUT)
    print("starting daemons")

    for ch in range(NUM_SERVOS):
        threading.Thread(
            target=servo_worker,
            args=(ch,),
            daemon=True
        ).start()
    threading.Thread(target=gpio_worker, daemon=True).start()

    threading.Thread(target=serial1_reader, args=(ser1,), daemon=True).start()
    threading.Thread(target=serial1_writer, args=(ser1,), daemon=True).start()

    threading.Thread(target=serial2_api, args=(ser2,), daemon=True).start()
    threading.Thread(target=serial2_writer, args=(ser2,), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown.set()

# ---------------- Entry ----------------

if __name__ == "__main__":
    main()
