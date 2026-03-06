import json
import os
import time
import threading
from queue import Queue
import serial

from adafruit_servokit import ServoKit

import RPi.GPIO as GPIO

# List of GPIO pins
swi_gpio_pins = [27, 18, 5, 6, 12, 13, 16, 19, 20, 21, 24, 22, 23, 25]

"""
SET <channel> <0|1>    -> OK | ERR BUSY
GET DATA               -> DATA <processed>
GET IO <ch>            -> get switch position

"""

# ---------------- Configuration ----------------

LIMITS_FILE = "servo_limits.json"
NUM_SERVOS = 14
MOVE_SPEED = 0.03
STEP_DEGREE = 1

SERIAL1_DEV = "/dev/ttyACM0" # USB to arduino, WARNING: opening this device will reset the board! 
SERIAL2_DEV = "/dev/ttyAMA0" # serial to second pi
BAUD1 = 115200
BAUD2 = 115200

RECEIVE_FRAMES = 1 # modify to get much more frames in a second (max 100), time between frames is 10ms
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

current_io_state = ["01" for i in range(NUM_SERVOS)]

servo_queues = [Queue() for _ in range(NUM_SERVOS)]
servo_busy   = [threading.Event() for _ in range(NUM_SERVOS)]

servo_event_q = Queue()

serial1_data = None
serial1_lock = threading.Lock()
adc_packet_counter = 0

shutdown = threading.Event()

# ---------------- Callbacks ----------------

def on_switch_start(channel):
    global current_io_state
    servo_event_q.put(f"IO B {channel} 00\n")
    current_io_state[channel] = "00"

def on_switch_end(channel, state):
    global current_io_state
    pos = "00"
    if state == True:
        pos = "10"
    else:
        pos = "01"
    servo_event_q.put(f"IO B {channel} {pos}\n")
    current_io_state[channel] = pos

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
    global current_io_state
    q = servo_queues[channel]

    while not shutdown.is_set():
        target,state = q.get()
        if (state == False and current_io_state[channel] == "01") or (state == True and current_io_state[channel] == "10"):
            continue # new state same as current

        servo_busy[channel].set()

        on_switch_start(channel)
        move_servo_smooth(channel, target)
        
        GPIO.output(swi_gpio_pins[channel],state) #set pin
        on_switch_end(channel, state)

        servo_busy[channel].clear()

# ---------------- gpio logic ----------------

def gpio_worker(channel):
    global current_io_state
    q = servo_queues[channel]

    while not shutdown.is_set():
        target,state = q.get()
        if (state == False and current_io_state[channel] == "01") or (state == True and current_io_state[channel] == "10"):
            continue

        if state == False: # open switch: fast
            GPIO.output(swi_gpio_pins[channel],state)
            on_switch_end(channel, state)
        else: # close switch: slow
            servo_busy[channel].set()
            on_switch_start(channel)
            time.sleep(MOVE_SPEED * 3.0) # arming the breaker is a bit slower
        
            GPIO.output(swi_gpio_pins[channel],state) #set pin

            on_switch_end(channel, state)

            servo_busy[channel].clear()


# ---------------- Public API ----------------

def set_switch(channel, state):
    if not (0 <= channel < NUM_SERVOS):
        return "ERR INVALID_CHANNEL\n"

    if servo_busy[channel].is_set():
        return "ERR BUSY\n"
    
    target = None
    if channel < 10:
        limits = servo_limits.get(str(channel))
        if not limits:
            return "ERR NO_LIMITS\n"

        target = limits["upper"] if state else limits["lower"]
        if target is None:
            return "ERR BAD_LIMIT\n"

    servo_queues[channel].put((target,state))
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


def serial1_writer(ser): # send message to the arduino we want some ADC packets
    n = RECEIVE_FRAMES
    while not shutdown.is_set():
        cmd = f"@ADC:{n}\n".encode()
        ser.write(cmd)
        time.sleep(1) # sleep for 1 second


def read_adc_packet(ser): # read message from arduino with ADC packets
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
    
    idx = 0
    
    # Decode ADCs
    adc = []
    for _ in range(ADC_NUM_CHANNELS):
        val = payload[idx] | (payload[idx + 1] << 8)
        adc.append(val)
        idx += 2
    
    # Decode short matrix (bitmasks)
    short_matrix = payload[idx:idx + ADC_WIRE_COUNT]
    idx += ADC_WIRE_COUNT
    
    # Decode relay measurements (6 channels)
    relay_measurements = []
    for _ in range(6):
        # WATCH OUT: Ensure there's enough data left
        if idx + 1 < len(payload):
            val = payload[idx] | (payload[idx + 1] << 8)
            relay_measurements.append(val)
            idx += 2
        else:
            print("Warning: Incomplete relay data")
            break
    
    return adc, short_matrix, relay_measurements


def format_packet_oneline(adc, short_matrix, relay_currents):
    # ADC values: decimal
    adc_part = "A" + ",".join(str(v) for v in adc)
    # Short matrix: 6 bytes as lowercase hex, 2 chars each
    short_part = "S" + ",".join(f"{b:02x}" for b in short_matrix)

    currents = "C" + ",".join(str(c) for c in relay_currents)
    return adc_part + " " + short_part + " " + currents

def serial1_reader(ser): # receive info from arduino
    global serial1_data
    global adc_packet_counter
    while not shutdown.is_set():
        pkt = read_adc_packet(ser)
        if not pkt:
            continue

        adc, shorts, relay_currents = pkt # adc, shorts = pkt
        processed = format_packet_oneline(adc, shorts, relay_currents)
        if adc_packet_counter % (10 * RECEIVE_FRAMES) == 0: # print very 10 seconds a packet
            print("ADC packet to be send: " + processed)
        adc_packet_counter += 1

        with serial1_lock:
            serial1_data = processed
            data = serial1_data or ""
            servo_event_q.put(f"DATA B {data}\n")

# ---------------- Serial2 API (slave) ----------------

def serial2_api(ser): # raspberry pi command receiver
    global current_io_state
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

        elif cmd[0] == "GET" and cmd[1] == "DATA":
            with serial1_lock:
                data = serial1_data or ""
            #ser.write(f"DATA {data}\n".encode())
            servo_event_q.put(f"DATA G {data}\n")

        elif cmd[0] == "GET" and cmd[1] == "IO":
            ch = int(cmd[2])
            if  (0 <= ch < NUM_SERVOS):
                state = current_io_state[ch]
                servo_event_q.put(f"IO G {ch} {state}\n") # 
            else:
                servo_event_q.put(f"ERR {ch} INVALID_CHANNEL\n") #


        else:
            msg= "ERR UNKNOWN_CMD\n"
            print("Unknown command: \'" + str(cmd) + "\'")
            servo_event_q.put(msg)
    GPIO.cleanup() 

# ---------------- Event reporter ----------------

def serial2_writer(ser): # response to raspberry pi
    while not shutdown.is_set():
        msg = servo_event_q.get()
        ser.write(msg.encode())
    GPIO.cleanup()

# ---------------- Startup ----------------

def main():
    ser1 = serial.Serial(SERIAL1_DEV, BAUD1, timeout=1) # arduino
    ser2 = serial.Serial(SERIAL2_DEV, BAUD2, timeout=1) # rly raspberry pi

    # prevent servo from moving quickly at init
    for chnl in range(NUM_SERVOS):
        limits = servo_limits.get(str(chnl))
        if not limits:
            print(f"Error: no limit found for channel {chnl}")
            continue
        default_angle = limits["lower"] # default is lower (off-state)
        if default_angle is None:
            print(f"Error: no lower limit for channel {chnl}")
            continue
        kit.servo[chnl].angle = int(default_angle)
        


    print("sleeping until arduino has been reset")
    time.sleep(ARDUINO_TIMEOUT)
    print("starting daemons")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in swi_gpio_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Initialize as OFF


    for ch in range(NUM_SERVOS):
        if ch < 10:
            threading.Thread(
                target=servo_worker,
                args=(ch,),
                daemon=True
            ).start()
        else:
            threading.Thread(
                target=gpio_worker,
                args=(ch,),
                daemon=True
            ).start()

    threading.Thread(target=serial1_reader, args=(ser1,), daemon=True).start() # arduino comm threats
    threading.Thread(target=serial1_writer, args=(ser1,), daemon=True).start() # 

    threading.Thread(target=serial2_api, args=(ser2,), daemon=True).start() # rly raspberry pi comm threats
    threading.Thread(target=serial2_writer, args=(ser2,), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown.set()
    finally:
        GPIO.cleanup()



# ---------------- Entry ----------------

if __name__ == "__main__":
    main()
