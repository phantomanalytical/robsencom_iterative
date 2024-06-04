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
        self.send_command(b'AT+EXIT\r\n')  # Ensure it's not in AT command mode
        self.send_command(b'+++\r\n')  # Enter AT command mode
        self.send_command(b'AT+MODE=2\r\n')  # Set to packet mode
        self.set_frequency(65)  # Set frequency to 915 MHz for both TX and RX
        self.set_power(22)  # Set the power to maximum
        self.set_spreading_factor(7)  # Set the default spreading factor
        self.set_coding_rate(1)  # Set the default coding rate
        self.send_command(b'AT+EXIT\r\n')  # Exit AT command mode
        print("Module initialized.")

    def send_command(self, command):
        self.ser.write(command)
        time.sleep(0.5)
        response = self.ser.read_all().decode('utf-8', errors='ignore')
        print(f"Sent command: {command.strip().decode()}, response: {response.strip()}")

    def set_frequency(self, channel):
        self.send_command(f'AT+TXCH={channel}\r\n'.encode())
        self.send_command(f'AT+RXCH={channel}\r\n'.encode())

    def set_power(self, power):
        self.send_command(f'AT+PWR={power}\r\n'.encode())

    def set_spreading_factor(self, sf):
        self.send_command(f'AT+SF={sf}\r\n'.encode())

    def set_coding_rate(self, cr):
        self.send_command(f'AT+CR={cr}\r\n'.encode())

    def set_network_id(self, net_id):
        self.send_command(f'AT+NETID={net_id}\r\n'.encode())

    def set_address(self, address):
        self.send_command(f'AT+ADDR={address}\r\n'.encode())

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
        else:
            print(f"Received data: {received_data}")
        return bytes(received_data)