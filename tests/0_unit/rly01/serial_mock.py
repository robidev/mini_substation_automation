#!/bin/env python3
# Create two linked pseudo-terminals
#socat -d -d PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0


import json
import os
import time
import threading
from queue import Queue
import serial


"""
SET <channel> <0|1>    -> OK | ERR BUSY
GET SERIAL1            -> DATA <processed>

SERVO <ch> <state>     -> event of position

"""

# ---------------- Configuration ----------------

NUM_SERVOS = 14
MOVE_SPEED = 0.03
STEP_DEGREE = 1

SERIAL2_DEV = "/tmp/ttyV1" # mock serial
BAUD2 = 115200

ARDUINO_TIMEOUT = 5.0

cur_state = ["01" for i in range(NUM_SERVOS)]

current = [90] * NUM_SERVOS

# ---------------- Shared state ----------------

servo_queues = [Queue() for _ in range(NUM_SERVOS)]
servo_busy   = [threading.Event() for _ in range(NUM_SERVOS)]

serial2_event_q = Queue()

serial1_data = None
serial1_lock = threading.Lock()

shutdown = threading.Event()

# ---------------- Callbacks ----------------

def on_switch_start(channel):
    global cur_state
    serial2_event_q.put(f"IO B {channel} 00\n")
    cur_state[channel] = "00"

def on_switch_end(channel, state):
    global cur_state
    pos = "00"
    if state == True:
        pos = "10"
    else:
        pos = "01"
    serial2_event_q.put(f"IO B {channel} {pos}\n")
    cur_state[channel] = pos

# ---------------- Servo logic ----------------

def move_servo_smooth(channel, target_angle):
    global current
    print(f"servo angle {current[channel]} at start")
    step = STEP_DEGREE if target_angle > current[channel] else -STEP_DEGREE

    for angle in range(int(current[channel]), int(target_angle), step):
        time.sleep(MOVE_SPEED)
    print(f"servo angle {target_angle} reached")
    current[channel] = target_angle

def servo_worker(channel):
    global cur_state
    q = servo_queues[channel]

    while not shutdown.is_set():
        target,state = q.get()

        servo_busy[channel].set()

        if (state == False and cur_state[channel] == "01") or (state == True and cur_state[channel] == "10"):
            print("new state same as current")
            servo_busy[channel].clear()
            continue

        on_switch_start(channel)
        if state == False: # moving to off postion
            print(f"GPIO: {channel} {state} (servo)") #set pin

        move_servo_smooth(channel, target)
        
        if state == True:
            print(f"GPIO: {channel} {state} (servo)") #set pin
        on_switch_end(channel, state)

        servo_busy[channel].clear()


def gpio_worker(channel):
    global cur_state
    q = servo_queues[channel]

    while not shutdown.is_set():
        target,state = q.get()

        servo_busy[channel].set()

        if (state == False and cur_state[channel] == "01") or (state == True and cur_state[channel] == "10"):
            print("new state same as current")
            servo_busy[channel].clear()
            continue

        on_switch_start(channel)
        if state == False: # moving to off postion
            print(f"GPIO: {channel} {state} (servo)") #set pin

        
        if state == True:
            time.sleep(3.0) #move_servo_smooth(channel, target)
            print(f"GPIO: {channel} {state} (servo)") #set pin
        on_switch_end(channel, state)

        servo_busy[channel].clear()

# ---------------- Public API ----------------

def set_switch(channel, state):
    if not (0 <= channel < NUM_SERVOS):
        return f"ERR {channel} INVALID_CHANNEL\n"

    if servo_busy[channel].is_set():
        return "ERR BUSY\n"
    target = 120 if state else 90
    servo_queues[channel].put((target,state))

    return "OK\n"

# ---------------- Serial1 reader ----------------


def format_packet_oneline():
    # ADC values: decimal
    feed1 = "0,0,0,"
    if cur_state[10] == "10":
        feed1 = "2,2,2,"
    
    adc_part = "A" + feed1 + "3,3,3,2,2,2,3,3,3"
    # Short matrix: 6 bytes as lowercase hex, 2 chars each
    short_part = "S01,02,03,04,05,06"
    return adc_part + " " + short_part

def serial1_reader_mock():
    global serial1_data
    while not shutdown.is_set():
        processed = format_packet_oneline()

        with serial1_lock:
            serial1_data = processed
            data = serial1_data or ""
            serial2_event_q.put(f"DATA B {data}\n")
        time.sleep(10)

# ---------------- Serial2 API (slave) ----------------

def serial2_api(ser):
    global serial1_data
    while not shutdown.is_set():
        line = ser.readline()
        if not line:
            continue

        cmd = line.decode(errors="ignore").strip().split()

        if not cmd:
            continue
        #print(f"cmd: {cmd}")
        if cmd[0] == "SET" and len(cmd) == 3:
            ch = int(cmd[1])
            state = cmd[2] == "1"
            serial2_event_q.put(set_switch(ch, state))

        elif cmd[0] == "GET" and cmd[1] == "DATA":
            with serial1_lock:
                data = serial1_data or ""
                serial2_event_q.put(f"DATA G {data}\n") # 

        elif cmd[0] == "GET" and cmd[1] == "IO":
            ch = int(cmd[2])
            if  (0 <= ch < NUM_SERVOS):
                state = cur_state[ch]
                serial2_event_q.put(f"IO G {ch} {state}\n") # 
            else:
                serial2_event_q.put(f"ERR {ch} INVALID_CHANNEL\n") #

        else:
            msg= b"ERR UNKNOWN_CMD\n"
            serial2_event_q.put(msg)

# ---------------- Event reporter ----------------

def serial2_writer(ser):
    while not shutdown.is_set():
        msg = serial2_event_q.get()
        ser.write(msg.encode())


# ---------------- Startup ----------------

def main():
    ser2 = serial.Serial(SERIAL2_DEV, BAUD2, timeout=1)

    print("sleeping until arduino has been reset")
    time.sleep(ARDUINO_TIMEOUT)
    print("starting daemons")

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

    threading.Thread(target=serial1_reader_mock, daemon=True).start()

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
