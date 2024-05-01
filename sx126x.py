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
        GPIO.output(self.M1, GPIO.HIGH)

        self.ser = serial.Serial(self.serial_n, 9600, timeout=1)
        self.ser.flushInput()

        self.set_module_settings()

    def set_module_settings(self):
        settings = bytearray([0xC0, self.addr & 0xFF, (self.addr >> 8) & 0xFF, self.net_id,
                              self.air_speed, self.buffer_size, self.power, 0x00, 0x00])
        self.ser.write(settings)

    def update_module_settings(self, freq=None, addr=None, power=None, air_speed=None, buffer_size=None):
        if freq is not None:
            self.freq = freq
        if addr is not None:
            self.addr = addr
        if power is not None:
            self.power = power
        if air_speed is not None:
            self.air_speed = air_speed
        if buffer_size is not None:
            self.buffer_size = buffer_size

        self.set_module_settings()

    def send(self, data):
        self.ser.write(data)
        if not self.wait_for_ack():
            print("No ACK received. Retrying...")
            self.ser.write(data)  # Retry sending the packet
            if not self.wait_for_ack():
                print("Retry failed. Check connection.")
                return False
        return True

    def wait_for_ack(self):
        start_time = time.time()
        timeout = 5  # seconds
        while time.time() - start_time < timeout:
            if self.ser.in_waiting:
                ack = self.ser.read(self.ser.in_waiting)
                if b'ACK' in ack:
                    return True
        return False

    def receive(self, timeout=120):
        received_data = bytearray()
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting:
                received_data += self.ser.read(self.ser.in_waiting)
                if b'END' in received_data:
                    self.ser.write(b'ACK')
                    break
            time.sleep(0.1)
        return bytes(received_data)

    def get_settings(self):
        GPIO.output(self.M1, GPIO.HIGH)
        self.ser.write(b'\xC1\x00\x09')
        time.sleep(0.1)  # wait for data to become available
        if self.ser.in_waiting:
            return self.ser.read(self.ser.in_waiting)
        return None

    def get_channel_rssi(self):
        self.ser.write(b'\xC1\x00\xC0\x00\x00')
        if self.ser.in_waiting:
            time.sleep(0.1)
            response = self.ser.read(self.ser.in_waiting)
            if len(response) >= 5:
                return -256 + response[4]
        return None
