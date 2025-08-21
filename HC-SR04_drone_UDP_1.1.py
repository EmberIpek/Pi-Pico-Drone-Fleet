# Author: Ember Ipek
# Date: 8/11/2025
# Preliminary proximity sensor data for eventual integration with a HS210 drone
# Data and checksum packed and sent to RPi through UDP

from machine import Pin, time_pulse_us
import time
import network
import socket
import struct

TRIGGER = Pin(2, Pin.OUT)
ECHO = Pin(3, Pin.IN)

# connect to mason wifi
ssid = "MASON"
wlan = network.WLAN(network.WLAN.IF_STA)
wlan.active(True)
wlan.connect(ssid)
while not wlan.isconnected():
    time.sleep(0.5)
print("Connected to Wi-Fi: ", wlan.ifconfig())

# UDP setup
UDP_IP = "10.166.174.71"  # IP of RPi
UDP_PORT = 5005
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def checkDist():
    # send pulse
    TRIGGER.value(0)
    time.sleep_us(2)
    TRIGGER.value(1)
    time.sleep_us(10)
    TRIGGER.value(0)
    
    # calculate distance in cm, speed of sound in air = 343m/s
    duration = time_pulse_us(ECHO, 1)
    if duration < 0:
        dist = -1
    dist = duration * (343 / 2) * (0.0001)
    
    return dist
    
#     while ECHO.value == 0:
#         pass
#     t1 = time.ticks_us()
#     while ECHO.value == 1:
#         pass
#     t2 = time.ticks_us()
#     # print("t1: ", t1, "t2: ", t2)
#     # calculate distance in cm, speed of sound in air = 343m/s
#     return (t2 - t1) * (343 / 2) * (0.01)


def calcChecksum(byte_data):
    checksum = 0
    
    for byte in byte_data:
        checksum ^= byte
    
    return checksum

# packs data for transmission over UDP and appends checksum
# < = little endian, B = unsigned char, h = signed short, H = unsigned short, f = float
def packData(id, seq, dist, accelX, accelY, accelZ, gyroX):
    packet = struct.pack("<Bhfhhhh", id, seq, dist, accelX, accelY, accelZ, gyroX)
    checksum = calcChecksum(packet)
    packet += struct.pack("<H", checksum)
    
    return packet

# maintain wifi connection
def maintainWifi():
    if not wlan.isconnected():
        print("Wi-Fi lost, reconnecting...")
        connect_wifi()
    
    return

seq = 0
droneId = 1

while True:
    maintainWifi()
    dist = checkDist()
    print("Distance: ", checkDist())
    # placeholder values for accel and gyro
    accel = (0, 0, 0)
    gyroX = 0
    
    packet = packData(droneId, seq, dist, accel[0], accel[1], accel[2], gyroX)

    s.sendto(packet, (UDP_IP, UDP_PORT))
    print("Packet sent")
    print(wlan.ifconfig())
    
    seq = (seq + 1) % 65536
    
    time.sleep(0.1)