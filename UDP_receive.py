import socket
import struct
import time
import RPi.GPIO as GPIO

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#change these later, these are SDA/SCL pins, might need
pinBackward = 7
pinForward = 11
GPIO.setup(pinBackward, GPIO.OUT)
GPIO.setup(pinForward, GPIO.OUT)
pwmBackward = GPIO.PWM(pinBackward, 1000)
pwmForward = GPIO.PWM(pinForward, 1000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Listening on port", UDP_PORT)
#move forward slowly
pwmForward.start(2)
pwmBackward.start(0)

while True:
    data, addr = sock.recvfrom(1024)
    #print("Received", len(data), "bytes from", addr)

    # > = big endian, f = float
    try:
        data = struct.unpack("<BhfhhhhH", data)
        distance = data[2]
        checksum = data[7]
        if(distance < 100):
            #slowly back away
            pwmForward.ChangeDutyCycle(0)
            pwmBackward.ChangeDutyCycle(20)
            #maybe rotate after? no sensor behind drone
        elif(distance >= 200):
            pwmForward.ChangeDutyCycle(5)
            pwmBackward.ChangeDutyCycle(0)
        print("UDP received! distance: ", distance)
    except struct.error:
        print("Packet unpacking failed")
    finally:
        GPIO.cleanup