#!/usr/bin/env python3
import json
import os
import sys
import termios
import tty
from adafruit_servokit import ServoKit

# Initialize 16-channel ServoKit (works for the Adafruit 16-channel PWM/Servo HAT)
kit = ServoKit(channels=16)

# Constants
NUM_SERVOS = 10
LIMITS_FILE = "servo_limits.json"

# Load or initialize limits
if os.path.exists(LIMITS_FILE):
    with open(LIMITS_FILE, "r") as f:
        servo_limits = json.load(f)
else:
    servo_limits = {str(ch): {"lower": None, "upper": None} for ch in range(NUM_SERVOS)}


def save_limits():
    """Save current servo limits to JSON file."""
    with open(LIMITS_FILE, "w") as f:
        json.dump(servo_limits, f, indent=2)
    print(f"✅ Limits saved to {LIMITS_FILE}")


def getch():
    """Read a single keypress without Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def move_servo(channel, angle):
    """Set servo to a specific angle."""
    angle = max(0, min(180, angle))
    kit.servo[channel].angle = angle
    print(f"Channel {channel} → {angle:.1f}°")
    return angle


def channel_menu():
    """Select servo channel to control."""
    while True:
        print("\nSelect a servo channel (0–9) or 'q' to quit:")
        ch = getch()
        if ch == "q":
            save_limits()
            print("Exiting...")
            sys.exit(0)
        elif ch.isdigit() and 0 <= int(ch) < NUM_SERVOS:
            servo_control(int(ch))
        else:
            print("Invalid input.")


def servo_control(channel):
    """Control a single servo interactively."""
    angle = 90
    move_servo(channel, angle)
    print(
        f"\nControlling channel {channel}."
        "\nUse 'a' (−5°), 'd' (+5°), 's' (set angle),"
        "\n'u' (save upper), 'l' (save lower), 'e' (exit channel)."
    )

    while True:
        key = getch()

        if key == "a":
            angle = move_servo(channel, angle - 5)
        elif key == "d":
            angle = move_servo(channel, angle + 5)
        elif key == "s":
            try:
                new_angle = float(input("Enter new angle (0–180): "))
                angle = move_servo(channel, new_angle)
            except ValueError:
                print("Invalid number.")
        elif key == "u":
            servo_limits[str(channel)]["upper"] = angle
            save_limits()
            print(f"🔼 Set upper limit for channel {channel} → {angle}°")
        elif key == "l":
            servo_limits[str(channel)]["lower"] = angle
            save_limits()
            print(f"🔽 Set lower limit for channel {channel} → {angle}°")
        elif key == "e":
            print(f"Returning to channel selection.")
            break
        elif key == "q":
            save_limits()
            print("Exiting...")
            sys.exit(0)
        else:
            print("Unknown key. Use 'a', 'd', 's', 'u', 'l', 'e', or 'q'.")


if __name__ == "__main__":
    print("=== Adafruit Servo HAT Calibration Tool ===")
    print("Controls 10 servos (channels 0–9)")
    print("Press 'q' anytime to quit.")
    channel_menu()

