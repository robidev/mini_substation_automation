#!/usr/bin/env python3
import json
import os
import threading
import time
from adafruit_servokit import ServoKit

# ===============================
# CONFIG
# ===============================
LIMITS_FILE = "servo_limits.json"
NUM_SERVOS = 10
MOVE_SPEED = 0.03   # delay between angle steps (smaller = faster)
STEP_DEGREE = 1     # degrees per step

# ===============================
# INITIALIZATION
# ===============================
kit = ServoKit(channels=16)

if not os.path.exists(LIMITS_FILE):
    raise FileNotFoundError(f"Limit file '{LIMITS_FILE}' not found. Run calibration tool first.")

with open(LIMITS_FILE, "r") as f:
    servo_limits = json.load(f)

# Track motion states
servo_moving = [False] * NUM_SERVOS


# ===============================
# HOOK FUNCTIONS (extend later)
# ===============================
def on_switch_start(channel, target_angle):
    print(f"🟡 Channel {channel}: starting movement to {target_angle}°")


def on_switch_end(channel, target_angle):
    print(f"✅ Channel {channel}: reached {target_angle}°")


# ===============================
# SERVO CONTROL
# ===============================
def _move_servo_thread(channel, target_angle):
    """Background thread: move servo smoothly to target."""
    global servo_moving
    servo_moving[channel] = True
    on_switch_start(channel, target_angle)

    servo = kit.servo[channel]
    current = servo.angle or 90  # fallback to 90 if angle unknown
    step = STEP_DEGREE if target_angle > current else -STEP_DEGREE

    for angle in range(int(current), int(target_angle), int(step)):
        servo.angle = angle
        time.sleep(MOVE_SPEED)

    servo.angle = target_angle  # ensure final
    on_switch_end(channel, target_angle)
    servo_moving[channel] = False


def set_switch(channel: int, state: bool):
    """
    Move servo for a given channel to upper (True) or lower (False) limit.
    Returns immediately; movement continues in background.
    """
    if channel < 0 or channel >= NUM_SERVOS:
        print("❌ Invalid channel number.")
        return

    if servo_moving[channel]:
        print(f"⚠️ Channel {channel} is busy, ignoring command.")
        return

    limits = servo_limits.get(str(channel))
    if not limits:
        print(f"⚠️ No limits defined for channel {channel}.")
        return

    target_angle = limits["upper"] if state else limits["lower"]
    if target_angle is None:
        print(f"⚠️ Missing {'upper' if state else 'lower'} limit for channel {channel}.")
        return

    # Start motion in separate thread
    threading.Thread(target=_move_servo_thread, args=(channel, target_angle), daemon=True).start()


# ===============================
# TEST SHELL
# ===============================
def main():
    print("=== Servo Switch Controller ===")
    print("Use 0–9 to select channel, then '1' (on) or '0' (off).")
    print("Press 'q' to quit.\n")

    while True:
        cmd = input("Enter command (e.g., 3 1): ").strip().lower()
        if cmd == "q":
            print("Exiting...")
            break

        try:
            ch, state = cmd.split()
            ch = int(ch)
            if state in ("1", "on", "true", "t"):
                set_switch(ch, True)
            elif state in ("0", "off", "false", "f"):
                set_switch(ch, False)
            else:
                print("❌ Invalid state. Use 1/on or 0/off.")
        except ValueError:
            print("❌ Invalid input. Use format: '<channel> <on/off>' or 'q' to quit.")


if __name__ == "__main__":
    main()
