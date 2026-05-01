# Pi Pico Drone Fleet Project
## 8/6/2025
## Ember Ipek

---

## A New Controller
**Experimentation/tinker phase**

8/6/2025
I had an idea for an AI controlled drone fleet that could fly in different formations and dynamically switch between defensive and offensive strategies depending on surroundings. Unsure of where to start, I just ordered the cheapest drone I could find on Amazon, the HS210. I opened it up to find a PAN7420S7FA chip, which I found out is a 2.4GHz Bluetooth transceiver. I figured I could interface with it using a Pi Pico W mounted onto the drone and route the 3.7V LiPo battery to power both the Pico and the drone. I also picked up an HC-SR04 ultrasonic sensor and powered it through the LiPo battery and connected the trigger pin to GP2 and the echo pin to GP3. I soldered this circuit onto a protoboard and had trouble getting readings from the sensor, but the drone is receiving power. Building the circuit on the breadboard, I was able to get readings and found that my soldering needed reworking.
Next step is to use a regular RPi to act as a “flight controller” for the Pico modified drone to implement a collision avoidance system. This would involve sending data packets to and from the Pico W using wifi. Once this is working, perhaps I would like to add an accelerometer and gyroscope as a DIY IMU to facilitate pitch and yaw control. Potential issues: wifi lag, processing power limitations, weight.
Documentation to read: Pin, machine.time_pulse_us(), struct.pack(), struct.unpack()
MPU6050 or MPU9250?

---

# Return of the RPi
**Handling data transfer and defining a protocol**

8/11/2025
Code updated to pack and send the data and checksum from the HC-SR04 sensor to the RPi using UDP. Set up static IP for RPi and cell phone hotspot for wifi communication (thanks, GMU client isolation). Next steps: unpack data on Pi side and figure out how to interface with the chip to send flight commands as a DIY flight controller.
Documentation to read: network.WLAN(), active(), connect(), isconnected(), ifconfig(), socket(), bind(), sendto(), and recvfrom()

---

# Attack of the Drones
**First attempts at autonomy**

4/28/2026

Project resumed, new (sturdier) wires soldered onto prototyping board:

<img width="975" height="731" alt="image" src="https://github.com/user-attachments/assets/794896dc-fc16-4d51-9f88-c2aad26b529f" />

Pico code will pack and send telemetry data to RPi. Current protocol for data packets is as follows: 1-byte ID, 2-byte packet sequence number, 4-byte HC-SR04 data, 2-byte accelerometer X data, 2-byte accelerometer Y data, 2-byte accelerometer Z data, 2-byte gyroscope X data, 2-byte checksum. RPi will unpack the data and send inputs to drone controller based on data. Pi 5 does not support Debian Bullseye, add os_check=0 in config.txt to override. UDP receive code on Pi successfully unpacks data according to protocol:

```terminal
UDP received! data:  (1, 348, 1206.2623291015625, 0, 0, 0, 0, 35)
Received 17 bytes from ('172.20.10.9', 53859)
UDP received! data:  (1, 349, 1206.2451171875, 0, 0, 0, 0, 144)
Received 17 bytes from ('172.20.10.9', 53859)
```

Received data is laggy, must synchronize data. Controller opened up, and found chip labeled 2512CTb, push buttons, and analog stick inputs. Measure input pin voltages to figure out operation of controller. Trigger buttons found to be active low with Vcc pin at 3.3V. Can connect button signal to a GPIO pin on Pi and set as input. To simulate button press, switch pin to output and pull LOW, and switch back to input. Right analog stick controls lateral and forward/backward movement: can use this for collision avoidance. VxJ1 pins sit at 58.5mV center and range from 1mV full right input – 80mV full left input. Likewise, VyJ1 rests at 58.5mV and ranges from 1mV up input – 80mV down. Can use PWM to simulate voltage level changes on joystick pins? Test output from PWM pins first.
Soldered wires onto controller. Test RPi control with PWM. Issue: can add to voltage, but how to subtract? Solution: raise ground. Using pin 2 to control forward motion of drone until obstacle detected. 1kHz frequency, duty cycle 0.2 = 6.6mV. Verify PWM voltages with multimeter first. Measured duty cycle 0 is 50mV. Pull-down resistor did nothing. Added 20M resistors in series, duty cycle 0 output is now ~18mV, duty cycle 0.2 is ~30mV, voltage differential is 12mV. Fast response from UDP receiver side for changes in distance.

UDP send/receive video:

[![Watch the video](https://img.youtube.com/vi/cnNgMN9ZORI/default.jpg)](https://youtu.be/cnNgMN9ZORI)




