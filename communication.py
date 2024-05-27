from sx126x import sx126x
import time

class LoRaComm:
    def __init__(self, address=36, serial_num='/dev/ttyACM0', net_id=0):
        self.lora = sx126x(serial_num=serial_num, net_id=net_id)
        self.lora.set_address(address)

    def update_settings(self, power=None, spreading_factor=None, coding_rate=None, address=None, network_id=None):
        if power is not None:
            self.lora.set_power(power)
        if spreading_factor is not None:
            self.lora.set_spreading_factor(spreading_factor)
        if coding_rate is not None:
            self.lora.set_coding_rate(coding_rate)
        if address is not None:
            self.lora.set_address(address)
        if network_id is not None:
            self.lora.set_network_id(network_id)

    def send_data(self, data, filename):
        print("Attempting to send data...")
        file_size = len(data)
        header = f"FILENAME:{filename},SIZE:{file_size}\n".encode()
        self.lora.send(header + data + b'END')
        print("Data sent.")

    def receive_data(self, timeout=300, save_path=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        header_received = False
        file_size = 0
        filename = ""

        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                received_data += data
                print(f"Received data chunk: {data}")

                if not header_received:
                    if b'\n' in received_data:
                        header, received_data = received_data.split(b'\n', 1)
                        header = header.decode()
                        if "FILENAME:" in header and "SIZE:" in header:
                            header_received = True
                            filename = header.split("FILENAME:")[1].split(",")[0]
                            file_size = int(header.split("SIZE:")[1])
                            print(f"Receiving file: {filename} of size {file_size} bytes")
                
                if header_received and len(received_data) >= file_size:
                    if b'END' in received_data[-3:]:
                        received_data = received_data[:-3]  # Remove the 'END' marker
                    break

            time.sleep(0.1)

        if header_received and save_path:
            with open(save_path, 'wb') as file:
                file.write(received_data[:file_size])
                print(f"Data successfully saved to '{save_path}'")
        elif header_received:
            with open(filename, 'wb') as file:
                file.write(received_data[:file_size])
                print(f"Data successfully saved to '{filename}'")

        if not header_received:
            print("Timeout reached without detecting the file header.")

        return bytes(received_data)