import serial
import time

class sx126x:
    def __init__(self, serial_num, address, net_id=0, crypt=0):
        self.serial_n = serial_num
        self.address = address
        self.net_id = net_id
        self.crypt = crypt
        self.ser = serial.Serial(self.serial_n, 115200, timeout=3)
        self.initialize()

    def initialize(self):
        self.ser.write(b'AT+EXIT\r\n')  # Ensure it's not in AT command mode
        self.ser.write(b'+++\r\n')  # Enter AT command mode
        time.sleep(1)  # Wait for the module to respond
        self.set_frequency(65)  # Set frequency to 915 MHz for both TX and RX
        self.set_power(22)  # Set the power to maximum
        self.set_spreading_factor(7)  # Set the default spreading factor
        self.set_coding_rate(1)  # Set the default coding rate
        self.set_address(self.address)  # Set the default address
        self.ser.write(b'AT+EXIT\r\n')  # Exit AT command mode

    def set_frequency(self, channel):
        self.ser.write(f'AT+TXCH={channel}\r\n'.encode())
        self.ser.write(f'AT+RXCH={channel}\r\n'.encode())

    def set_power(self, power):
        self.ser.write(f'AT+PWR={power}\r\n'.encode())

    def set_spreading_factor(self, sf):
        self.ser.write(f'AT+SF={sf}\r\n'.encode())

    def set_coding_rate(self, cr):
        self.ser.write(f'AT+CR={cr}\r\n'.encode())

    def set_address(self, address):
        self.ser.write(f'AT+ADDR={address}\r\n'.encode())

    def set_network_id(self, net_id):
        self.ser.write(f'AT+NETID={net_id}\r\n'.encode())

    def send(self, data):
        self.ser.write(data + b'\r\n')  # Send data followed by a new line
        time.sleep(1)  # Allow some time for data to be sent
        print("Data sent successfully.")

    def receive(self, timeout=300):
        print("Receiving data...")
        start_time = time.time()
        received_data = bytearray()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting:
                data = self.ser.read(self.ser.in_waiting)
                received_data += data
            time.sleep(0.1)
        print("Timeout reached without receiving complete data.")
        return bytes(received_data)