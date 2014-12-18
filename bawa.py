__author__ = 'dheepan'

import sys
from time import sleep
import subprocess

bat_state_file = "/proc/acpi/battery/BAT0/state"
bat_info_file = "/proc/acpi/battery/BAT0/info"
LOW_BATTERY_TRIGGER = 30
HIGH_BATTERY_TRIGGER = 30
TIMER = 120 # seconds
# todo change print to debug print
# todo Sleep timer should be learning!


def discharging(remaining, discharge_rate, max_cap, iswarned):
    time_left = float(remaining) / discharge_rate
    remaining_percent = int((remaining * 100) / max_cap)
    hours = int(time_left)
    minutes = int((time_left - hours) * 60)
    low_battery_message = "Remaining time is {0} hours and {1} minutes - {2}%".format(str(hours), str(minutes), str(
        remaining_percent))
    if remaining_percent <= LOW_BATTERY_TRIGGER and not iswarned:
        subprocess.call(["/usr/bin/notify-send", "Battery low", low_battery_message])
        subprocess.call(["aplay", '/usr/share/sounds/linuxmint-logout.wav', "-q"])
        iswarned = True
    sys.stdout.flush()
    return iswarned


def charging(remaining, charging_rate, max_cap, iswarned):
    time_left = float(max_cap - remaining) / charging_rate
    remaining_percent = int((remaining * 100) / max_cap)
    hours = int(time_left)
    minutes = int((time_left - hours) * 60)
    charged_battery_message = "Remaining time is {0} hours and {1} minutes - {2}%".format(str(hours), str(minutes), str(
        remaining_percent))
    if remaining_percent >= HIGH_BATTERY_TRIGGER and not iswarned:
        subprocess.call(["/usr/bin/notify-send", "Battery charged", charged_battery_message])
        subprocess.call(["aplay", '/usr/share/sounds/linuxmint-logout.wav', "-q"])
        iswarned = True
    # todo Guess remaining time based on previous pattern
    sys.stdout.flush()
    return iswarned


try:
    isNotified = False
    previous_state = True # 0 refers to not charging and 1 is charging
    while(True):
        with open(bat_state_file) as state:
            state.seek(0)
            for line_s in state:
                data = line_s.split(":")[1].strip().split(" ")[0]
                if "present rate" in line_s:
                    rate = int(data)
                elif "remaining capacity" in line_s:
                    remaining_cap = int(data)
                elif "charging state" in line_s:
                    if data == "charging":
                        print("charging")
                        isCharging = True
                    elif data == "discharging":
                        print("Discharging")
                        isCharging = False
        with open(bat_info_file) as info:
            info.seek(0)
            for line in info:
                data = line.split(":")[1].strip().split(" ")[0]
                if "last full capacity" in line:
                    max_capacity = int(data)

        if previous_state != isCharging:
            isNotified = False
            print("previous state not the same")

        if not isCharging:
            isNotified = discharging(remaining_cap, rate, max_capacity, isNotified)
            print(isNotified)
            previous_state = False
        elif isCharging:
            isNotified = charging(remaining_cap, rate, max_capacity, isNotified)
            print(isNotified)
            previous_state = True
        sleep(TIMER)

except KeyboardInterrupt:
    print("Exiting")