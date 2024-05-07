import RPi.GPIO as GPIO
import serial
import time

class sx126x:
    def __init__(self, serial_num, freq, addr, power, rssi, air_speed=2400, net_id=0, buffer_size=240, crypt=0, relay=False, lbt=False, wor=False):
        self.M0 = 22
        self.M1 = 27
        self.serial_n = serial_num
        self.freq = freq
        self.addr = addr
        self.power = power
        self.air_speed = air_speed
        self.net_id = net_id
        self.buffer_size = buffer_size
        self.crypt = crypt
        self.relay = relay
        self.lbt = lbt
        self.wor = wor

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.LOW)

        self.ser = serial.Serial(self.serial_n, 9600, timeout=3)
        self.ser.flushInput()

        self.update_module_settings()

    def update_module_settings(self):
        settings = bytearray([0xC0, self.addr & 0xFF, (self.addr >> 8) & 0xFF, self.net_id, 0x60,
                              0x00, 0x00, 0x00, 0x00])  # Assuming air_speed of 9600, packet size of 240 bytes, power of 22dBm
        self.ser.write(settings)

    def send(self, data):
        print("Sending data...")
        self.ser.write(data)
        time.sleep(1)  # Allow some time for data to be sent and received
        print("Data sent successfully.")

    def receive(self, timeout=120):
        print("Receiving data...")
        start_time = time.time()
        received_data = bytearray()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting:
                data = self.ser.read(self.ser.in_waiting)
                received_data += data
                if b'END' in received_data:  # Check for end marker in data
                    print("End of transmission detected.")
                    return bytes(received_data)
            time.sleep(0.1)
        print("Timeout reached without receiving complete data.")
        return None
