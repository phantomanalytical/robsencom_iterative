import serial
import time

class sx126x:
    def __init__(self, serial_num, net_id=0, crypt=0):
        self.serial_n = serial_num
        self.net_id = net_id
        self.crypt = crypt
        self.ser = serial.Serial(self.serial_n, 115200, timeout=3)
        self.initialize()

    def enter_at_mode(self):
        self.ser.write(b'+++\r\n')
        time.sleep(1)  # Wait for the module to respond
        response = self.ser.read_all().decode('utf-8', errors='ignore')
        print(f"Entered AT mode, response: {response.strip()}")

    def exit_at_mode(self):
        self.ser.write(b'AT+EXIT\r\n')
        time.sleep(0.5)
        response = self.ser.read_all().decode('utf-8', errors='ignore')
        print(f"Exited AT mode, response: {response.strip()}")

    def initialize(self):
        print("Initializing module...")
        self.enter_at_mode()
        self.send_command(b'AT+SF=7\r\n')  # Spreading Factor = 7
        self.send_command(b'AT+BW=0\r\n')  # Bandwidth = 125KHz
        self.send_command(b'AT+CR=1\r\n')  # Encoding Rate = 4/5
        self.send_command(b'AT+PWR=22\r\n')  # Set Power to Low Value
        self.send_command(b'AT+NETID=0\r\n')  # Network ID = 0
        self.send_command(b'AT+LBT=0\r\n')  # Disable LBT
        self.send_command(b'AT+MODE=2\r\n')  # Packet Mode
        self.send_command(b'AT+TXCH=65\r\n')  # Transmit Channel = 915 MHz
        self.send_command(b'AT+RXCH=65\r\n')  # Receive Channel = 915 MHz
        self.send_command(b'AT+RSSI=0\r\n')  # Set the RSSI to disabled
        self.send_command(b'AT+PORT=3\r\n')  # Set Port to RS232
        self.send_command(b'AT+BAUD=115200\r\n')  # Set baudrate to 115200
        self.send_command(b'AT+COMM="8N1"\r\n')  # Set Com port parameters 8N1
        self.send_command(b'AT+KEY=0\r\n')  # Disable encryption
        self.exit_at_mode()
        print("Module initialized.")

    def send_command(self, command):
        self.ser.write(command)
        time.sleep(0.5)
        response = self.ser.read_all().decode('utf-8', errors='ignore')
        print(f"Sent command: {command.strip().decode()}, response: {response.strip()}")

    def set_frequency(self, channel):
        self.enter_at_mode()
        self.send_command(f'AT+TXCH={channel}\r\n'.encode())
        self.send_command(f'AT+RXCH={channel}\r\n'.encode())
        self.exit_at_mode()

    def set_power(self, power):
        self.enter_at_mode()
        self.send_command(f'AT+PWR={power}\r\n'.encode())
        self.exit_at_mode()

    def set_spreading_factor(self, sf):
        self.enter_at_mode()
        self.send_command(f'AT+SF={sf}\r\n'.encode())
        self.exit_at_mode()

    def set_coding_rate(self, cr):
        self.enter_at_mode()
        self.send_command(f'AT+CR={cr}\r\n'.encode())
        self.exit_at_mode()

    def set_network_id(self, net_id):
        self.enter_at_mode()
        self.send_command(f'AT+NETID={net_id}\r\n'.encode())
        self.exit_at_mode()

    def set_address(self, address):
        self.enter_at_mode()
        self.send_command(f'AT+ADDR={address}\r\n'.encode())
        self.exit_at_mode()

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
        if not received_data:
            print("Timeout reached without receiving complete data.")
        else:
            print(f"Received data: {received_data}")
        return bytes(received_data)