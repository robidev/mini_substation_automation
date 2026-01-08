/*
sudo apt update
sudo apt install pigpio
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

Install JSON library:

sudo apt install nlohmann-json3-dev

*/

#include <iostream>
#include <fstream>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>
#include <cmath>

#include <pigpio.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

constexpr int NUM_SERVOS = 10;
constexpr float MOVE_SPEED = 0.03f;  // seconds
constexpr int STEP_DEGREE = 1;
constexpr int PCA9685_ADDR = 0x40;

std::atomic<bool> servo_moving[NUM_SERVOS];
json servo_limits;

/* Convert angle (0–180) to PWM pulse width (µs) */
int angle_to_pulse(int angle)
{
    return 500 + (angle * 2000 / 180);
}

void on_switch_start(int channel, int target)
{
    std::cout << "Channel " << channel
              << ": starting movement to "
              << target << "°\n";
}

void on_switch_end(int channel, int target)
{
    std::cout << "Channel " << channel
              << ": reached "
              << target << "°\n";
}

void move_servo_thread(int channel, int target_angle)
{
    servo_moving[channel] = true;
    on_switch_start(channel, target_angle);

    int current_angle = 90;
    int step = (target_angle > current_angle) ? STEP_DEGREE : -STEP_DEGREE;

    for (int angle = current_angle;
         angle != target_angle;
         angle += step)
    {
        gpioServo(channel, angle_to_pulse(angle));
        std::this_thread::sleep_for(
            std::chrono::milliseconds(
                static_cast<int>(MOVE_SPEED * 1000)
            )
        );
    }

    gpioServo(channel, angle_to_pulse(target_angle));
    on_switch_end(channel, target_angle);
    servo_moving[channel] = false;
}

void set_switch(int channel, bool state)
{
    if (channel < 0 || channel >= NUM_SERVOS)
    {
        std::cerr << "Invalid channel number\n";
        return;
    }

    if (servo_moving[channel])
    {
        std::cout << "Channel " << channel
                  << " is busy, ignoring command.\n";
        return;
    }

    if (!servo_limits.contains(std::to_string(channel)))
    {
        std::cerr << "No limits for channel "
                  << channel << "\n";
        return;
    }

    auto limits = servo_limits[std::to_string(channel)];
    int target_angle = state
                       ? limits["upper"].get<int>()
                       : limits["lower"].get<int>();

    std::thread(move_servo_thread, channel, target_angle).detach();
}

int main()
{
    if (gpioInitialise() < 0)
    {
        std::cerr << "pigpio init failed\n";
        return 1;
    }

    std::ifstream f("servo_limits.json");
    if (!f)
    {
        std::cerr << "Limit file not found\n";
        return 1;
    }

    f >> servo_limits;

    for (int i = 0; i < NUM_SERVOS; ++i)
        servo_moving[i] = false;

    set_switch(1, true);
    std::this_thread::sleep_for(std::chrono::seconds(10));
    set_switch(1, false);

    gpioTerminate();
    return 0;
}


/*

g++ servo_control.cpp -o servo_control -lpigpio -lpthread
sudo ./servo_control


*/