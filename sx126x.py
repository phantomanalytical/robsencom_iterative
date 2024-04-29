import RPi.GPIO as GPIO
import serial
import time

class sx126x:

    def __init__(self, serial_num, freq, addr, power, rssi, air_speed=2400, net_id=0, buffer_size=240, crypt=0, relay=False, lbt=False, wor=False):
        self.M0 = 22
        self.M1 = 27
        self.cfg_reg = [0xC2,0x00,0x09,0x00,0x00,0x00,0x62,0x00,0x12,0x43,0x00,0x00]
        self.start_freq = 915
        self.offset_freq = 18
        self.power = power
        self.air_speed = air_speed

        self.UART_BAUDRATE = {
            1200: 0x00,
            2400: 0x20,
            4800: 0x40,
            9600: 0x60,
            19200: 0x80,
            38400: 0xA0,
            57600: 0xC0,
            115200: 0xE0
        }
        self.PACKET_SIZE = {
            240: 0x00,
            128: 0x40,
            64: 0x80,
            32: 0xC0
        }
        self.POWER_SETTING = {
            22: 0x00,
            17: 0x01,
            13: 0x02,
            10: 0x03
        }

        self.serial_n = serial_num
        self.freq = freq
        self.addr = addr
        self.rssi = rssi
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

        self.ser = serial.Serial(serial_num, 9600)
        self.ser.flushInput()
        self.set_module_settings()


    def set_module_settings(self):
        # Basic configuration of the module
        settings = bytearray([0xC0, self.addr & 0xFF, (self.addr >> 8) & 0xFF, self.net_id, self.UART_BAUDRATE[self.air_speed],
                              self.PACKET_SIZE[self.buffer_size], self.POWER_SETTING[self.power], 0x00, 0x00])
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

        settings = bytearray([0xC0, self.addr & 0xFF, (self.addr >> 8) & 0xFF, self.net_id, self.UART_BAUDRATE[self.air_speed], self.PACKET_SIZE[self.buffer_size], self.POWER_SETTING[self.power], 0x00, 0x00])
        self.ser.write(settings)

    def send(self, data):
        # Packet sending with ACK handling
        if not self.send_packet(data):
            print("Sending failed, retrying...")
            self.send_packet(data)

    def send_packet(self, data):
        self.ser.write(data)
        return self.wait_for_ack()

    def wait_for_ack(self):
        start_time = time.time()
        timeout = 5
        while time.time() - start_time < timeout:
            if self.ser.in_waiting:
                response = self.ser.read(self.ser.in_waiting)
                if b'ACK' in response:
                    return True
        return False

    def receive(self):
        # Receive data packets
        start_time = time.time()
        timeout = 120
        received_data = bytearray()
        while True:
            if self.ser.in_waiting:
                received_data += self.ser.read(self.ser.in_waiting)
                if b'END' in received_data:
                    self.ser.write(b'ACK')
                    break
            if time.time() - start_time > timeout:
                break
            time.sleep(0.1)
        return bytes(received_data)

    def get_settings(self):
        # Retrieve settings from the module
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(0.1)
        self.ser.write(b'\xC1\x00\x09')
        if self.ser.in_waiting:
            time.sleep(0.1)
            return self.ser.read(self.ser.in_waiting)
        return None

    def get_channel_rssi(self):
        # Get channel RSSI
        self.ser.write(b'\xC1\x00\xC0\x00\x00')
        if self.ser.in_waiting:
            time.sleep(0.1)
            response = self.ser.read(self.ser.in_waiting)
            if len(response) >= 5:
                return -256 + response[4]
        return None
