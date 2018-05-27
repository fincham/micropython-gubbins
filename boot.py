"""
Handles standard bring-up tasks like configuring the WiFi. Install as 'boot.py' in filesystem root.

Michael Fincham <michael@hotplate.co.nz> 2018-05-25
"""

import machine
import network
import ntptime
import ujson
import usocket
import ustruct
import utime

settings = {}

def better_ntp():
    NTP_DELTA = 3155673600
    host = "pool.ntp.org"
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1b
    addr = usocket.getaddrinfo(host, 123)[0][-1]
    with usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM) as s:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    local_time = utime.localtime(ustruct.unpack("!I", msg[40:44])[0] - NTP_DELTA)
    local_time = local_time[0:3] + (0,) + local_time[3:6] + (0,)
    machine.RTC().datetime(local_time)

def setup():
    done = False
    while not done:
        print("Current values of settings:")
        print("")
        for key, value in settings.items():
            print("    %s = %s" % (key, value))
        print("")
        try:
            edit_key = input("Name of setting to change (or ^D to finish): ")
        except EOFError:
            print("")
            done = True
            continue
        if edit_key in settings:
            try:
                edit_value = input("New value or setting: ")
            except EOFError:
                print("")
                print("Cancelled.")
                continue

            settings[edit_key] = edit_value

    with open('settings.json', 'w') as settings_file:
        ujson.dump(settings, settings_file)

    print("Settings saved.")

if __name__ == "__main__":
    default_settings = {
        'ssid': None,
        'psk': None,
    }

    print("*** Hotplate gubbins booting...") 
    
    try:
        with open('settings.json', 'r') as settings_file:
            settings = ujson.load(settings_file)
    except:
        settings = default_settings.copy()
        print("Warning: no settings found, running setup")
        setup()

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(settings['ssid'], settings['psk'])
    print("Connecting to WiFi...", end='')
    while not sta_if.isconnected():
        print('.')
        utime.sleep_ms(500)
    print(" ok")

    print("Get NTP Time")
    better_ntp()
    print(utime.localtime())
