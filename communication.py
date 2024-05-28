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
        chunk_size = 240  # Define chunk size
        header = f"FILENAME:{filename},SIZE:{file_size}\n".encode('utf-8')
        
        # Send the header
        self.lora.send(header)

        # Split data into chunks and send each chunk
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            self.lora.send(chunk)
            time.sleep(0.1)  # Small delay between chunks

        # Send end marker
        self.lora.send(b'END_OF_FILE')
        print("Data sent.")

    def receive_data(self, timeout=300, save_path=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        header_received = False
        file_size = 0
        filename = ""
        transmission_ended = False

        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                received_data += data
                print(f"Received data chunk: {data}")

                if not header_received:
                    if b'\n' in received_data:
                        header, received_data = received_data.split(b'\n', 1)
                        header = header.decode('utf-8')
                        if "FILENAME:" in header and "SIZE:" in header:
                            header_received = True
                            filename = header.split("FILENAME:")[1].split(",")[0]
                            file_size = int(header.split("SIZE:")[1])
                            print(f"Receiving file: {filename} of size {file_size} bytes")

                if header_received and b'END_OF_FILE' in received_data:
                    received_data = received_data.split(b'END_OF_FILE')[0]
                    transmission_ended = True
                    print("End of transmission detected.")
                    break

            time.sleep(0.1)

        if transmission_ended and save_path:
            with open(save_path, 'wb') as file:
                file.write(received_data)
                print(f"Data successfully saved to '{save_path}'")
        elif transmission_ended:
            save_path = f'/home/images/{filename}'
            with open(save_path, 'wb') as file:
                file.write(received_data)
                print(f"Data successfully saved to '{save_path}'")

        if not transmission_ended:
            print("Timeout reached without detecting end of transmission.")

        return bytes(received_data)