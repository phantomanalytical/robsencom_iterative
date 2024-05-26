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


    def __init__(self, serial_num='/dev/bus/usb/001/003', freq, addr, power, rssi, air_speed=2400, net_id=0, buffer_size=240, crypt=0, relay=False, lbt=False, wor=False):
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

        self.ser = serial.Serial(self.serial_n, 9600, timeout=3)
        self.ser.flushInput()

        self.update_module_settings()

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

        settings = bytearray([0xC0, self.addr & 0xFF, (self.addr >> 8) & 0xFF, self.net_id,
                              self.UART_BAUDRATE[self.air_speed], self.PACKET_SIZE[self.buffer_size],
                              self.POWER_SETTING[self.power], 0x00, 0x00])
        self.ser.write(settings)
        print("Module settings updated.")


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
