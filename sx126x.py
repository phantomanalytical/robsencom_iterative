import serial
import time

class sx126x:
    def __init__(self, serial_num, net_id=0, crypt=0):
        self.serial_n = serial_num
        self.net_id = net_id
        self.crypt = crypt
        self.ser = serial.Serial(self.serial_n, 115200, timeout=3)
        self.initialize()

    def initialize(self):
        print("Initializing module...")
        self.ser.write(b'AT+EXIT\r\n')  # Ensure it's not in AT command mode
        time.sleep(0.5)
        self.ser.write(b'+++\r\n')  # Enter AT command mode
        time.sleep(1)  # Wait for the module to respond
        self.ser.write(b'AT+MODE=2\r\n')  # Set to packet mode
        time.sleep(0.5)
        self.set_frequency(65)  # Set frequency to 915 MHz for both TX and RX
        time.sleep(0.5)
        self.set_power(22)  # Set the power to maximum
        time.sleep(0.5)
        self.set_spreading_factor(7)  # Set the default spreading factor
        time.sleep(0.5)
        self.set_coding_rate(1)  # Set the default coding rate
        time.sleep(0.5)
        self.ser.write(b'AT+EXIT\r\n')  # Exit AT command mode
        time.sleep(0.5)
        print("Module initialized.")

    def set_frequency(self, channel):
        self.ser.write(f'AT+TXCH={channel}\r\n'.encode())
        time.sleep(0.1)
        self.ser.write(f'AT+RXCH={channel}\r\n'.encode())
        time.sleep(0.1)

    def set_power(self, power):
        self.ser.write(f'AT+PWR={power}\r\n'.encode())
        time.sleep(0.1)

    def set_spreading_factor(self, sf):
        self.ser.write(f'AT+SF={sf}\r\n'.encode())
        time.sleep(0.1)

    def set_coding_rate(self, cr):
        self.ser.write(f'AT+CR={cr}\r\n'.encode())
        time.sleep(0.1)

    def set_network_id(self, net_id):
        self.ser.write(f'AT+NETID={net_id}\r\n'.encode())
        time.sleep(0.1)

    def set_address(self, address):
        self.ser.write(f'AT+ADDR={address}\r\n'.encode())
        time.sleep(0.1)

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
                if b'END_OF_FILE' in received_data:
                    break
            time.sleep(0.1)
        if not received_data:
            print("Timeout reached without receiving complete data.")
        return bytes(received_data)