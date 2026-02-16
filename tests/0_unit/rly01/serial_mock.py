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
    feed2 = "0,0,0,"
    tr1 = "0,0,0,"
    tr2 = "0,0,0"

#    bus1 = int(0)
#    bus2 = int(0)
#    busdiv1 = int(0)
#    busdiv2 = int(0)
#
#    if cur_state[12] == "10" and cur_state[6] == "10": # Tr1 to bus1
#        bus1 += 900
#    if cur_state[12] == "10" and cur_state[7] == "10": # Tr1 to bus2
#        bus2 += 920
#    if cur_state[13] == "10" and cur_state[8] == "10": # Tr2 to bus1
#        bus1 += 940
#    if cur_state[13] == "10" and cur_state[9] == "10": # Tr2 to bus2
#        bus2 += 960
#
#
#    if cur_state[0] == "10" and cur_state[10] == "10" and cur_state[2] == "10": # bus1 to feed1
#        busdiv1 += 1
#    if cur_state[0] == "10" and cur_state[10] == "10" and cur_state[3] == "10": # bus2 to feed1
#        busdiv2 += 1	
#    if cur_state[1] == "10" and cur_state[11] == "10" and cur_state[4] == "10": # bus1 to feed2
#        busdiv1 += 1
#    if cur_state[1] == "10" and cur_state[11] == "10" and cur_state[5] == "10": # bus2 to feed2
#        busdiv2 += 1
#
#    f1total = int(0)
#    f2total = int(0)
#    t1total = int(0)
#    t2total = int(0)
#    if busdiv1 > 0: # something is connected to bus1
#        #feed 1
#        if cur_state[0] == "10" and cur_state[10] == "10" and cur_state[2] == "10": # feed 1 connected to bus1
#            f1total += bus1 / busdiv1 # busdiv can be 1 if only connected to feed 1 or 2 if also connected to feed 2, so divide current
#        if cur_state[1] == "10" and cur_state[11] == "10" and cur_state[4] == "10": # feed 2 connected to bus1
#            f2total += bus1 / busdiv1 # busdiv can be 1 if only connected to feed 1 or 2 if also connected to feed 2, so divide current
#        if cur_state[12] == "10" and cur_state[6] == "10": # Tr1 to bus1
#            t1total += 900
#        if cur_state[13] == "10" and cur_state[8] == "10": # Tr2 to bus1
#            t2total += 940
#
#
#    if busdiv2 > 0: # something is connected to bus1
#        #feed 1
#        if cur_state[0] == "10" and cur_state[10] == "10" and cur_state[3] == "10": # feed 1 connected to bus2
#            f1total += bus2 / busdiv2 # busdiv can be 1 if only connected to feed 1 or 2 if also connected to feed 2, so divide current
#        if cur_state[1] == "10" and cur_state[11] == "10" and cur_state[5] == "10": # feed 2 connected to bus2
#            f2total += bus2 / busdiv2 # busdiv can be 1 if only connected to feed 1 or 2 if also connected to feed 2, so divide current
#        if cur_state[12] == "10" and cur_state[7] == "10": # Tr1 to bus2
#            t1total += 920
#        if cur_state[13] == "10" and cur_state[9] == "10": # Tr2 to bus2
#            t2total += 960          
#
    f1total = int(0)
    f2total = int(0)
    t1total = int(0)
    t2total = int(0)
    bus1 = int(0)
    bus2 = int(0)

    if cur_state[0] == "10" and cur_state[10] == "10":
        f1total = 900
    if cur_state[1] == "10" and cur_state[11] == "10":
        f2total = 910

    if cur_state[2] == "10": # bus1 from feed1
        bus1 = f1total
    if cur_state[3] == "10": # bus2 from feed1
        bus2 = f1total
    if cur_state[4] == "10": # bus1 from feed2
        bus1 = f2total
    if cur_state[5] == "10": # bus2 from feed2
        bus2 = f2total
    
    if cur_state[12] == "10" and cur_state[6] == "10": # Tr1 from bus1
        t1total = bus1
    if cur_state[12] == "10" and cur_state[7] == "10": # Tr1 from bus2
        t1total = bus2
    if cur_state[13] == "10" and cur_state[8] == "10": # Tr2 from bus1
        t2total = bus1
    if cur_state[13] == "10" and cur_state[9] == "10": # Tr2 from bus2
        t2total = bus2

    feed1 = (str(int(f1total)) + ",") * 3
    feed2 = (str(int(f2total)) + ",") * 3
    tr1 = (str(int(t1total)) + ",") * 3
    tr2 = (str(int(t2total)) + ",") * 3
    tr2 = tr2[:-1]

    adc_part = "A" + feed1 + feed2 + tr1 + tr2
    # Short matrix: 6 bytes as lowercase hex, 2 chars each
    short_part = "S00,00,00,00,00,00"

    current = "C100,100,100,0,0,0"

    return adc_part + " " + short_part + " " + current

def serial1_reader_mock():
    global serial1_data
    while not shutdown.is_set():
        processed = format_packet_oneline()

        with serial1_lock:
            serial1_data = processed
            data = serial1_data or ""
            serial2_event_q.put(f"DATA B {data}\n")
        time.sleep(1)

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
