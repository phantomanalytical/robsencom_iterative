import RPi.GPIO as GPIO
import serial
import time

class sx126x:
    UART_BAUDRATE = {
        1200: 0x00,
        2400: 0x20,
        4800: 0x40,
        9600: 0x60,
        19200: 0x80,
        38400: 0xA0,
        57600: 0xC0,
        115200: 0xE0
    }

    PACKET_SIZE = {
        240: 0x00,
        128: 0x40,
        64: 0x80,
        32: 0xC0
    }

    POWER_SETTING = {
        22: 0x00,
        17: 0x01,
        13: 0x02,
        10: 0x03
    }

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
        self.rssi = rssi

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)
        self.set_normal_mode()  # Setting module to normal operation mode initially

        self.ser = serial.Serial(self.serial_n, 9600, timeout=3)
        self.ser.flushInput()

        self.update_module_settings()

    def set_normal_mode(self):
        """Set module to normal operation mode (M0=0, M1=0)."""
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.LOW)
        time.sleep(0.1)

    def update_module_settings(self):
        """Update the module's settings based on current attributes."""
        settings = bytearray([0xC0, self.addr & 0xFF, (self.addr >> 8) & 0xFF, self.net_id,
                              self.UART_BAUDRATE[self.air_speed], self.PACKET_SIZE[self.buffer_size],
                              self.POWER_SETTING[self.power], 0x00, 0x00])
        self.ser.write(settings)

    def send(self, data):
        """Send data and wait for an ACK."""
        self.set_normal_mode()  # Ensure it's in normal mode to send
        self.ser.write(data)
        return self.wait_for_ack()

    def wait_for_ack(self):
        """Wait for an ACK from the receiver."""
        start_time = time.time()
        while time.time() - start_time < 5:  # Wait for up to 5 seconds for an ACK
            if self.ser.in_waiting:
                response = self.ser.read(self.ser.in_waiting)
                if b'ACK' in response:
                    return True
        return False

    def receive(self, timeout=120):
        """Receive data until 'END' marker is found or timeout."""
        self.set_normal_mode()  # Ensure it's in normal mode to receive
        received_data = bytearray()
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting:
                received_data += self.ser.read(self.ser.in_waiting)
                if b'END' in received_data:
                    self.ser.write(b'ACK')
                    break
        return bytes(received_data)

    def get_channel_rssi(self):
        """Get channel RSSI."""
        self.set_normal_mode()  # Ensure it's in normal mode to check RSSI
        self.ser.write(b'\xC1\x00\xC0\x00\x00')
        if self.ser.in_waiting:
            time.sleep(0.1)
            response = self.ser.read(self.ser.in_waiting)
            if len(response) >= 5:
                return -256 + response[4]
        return None
