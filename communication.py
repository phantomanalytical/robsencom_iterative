from sx126x import sx126x
import time
import hashlib

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
        chunk_size = 240
        num_chunks = (file_size + chunk_size - 1) // chunk_size
        header = f"FILENAME:{filename},SIZE:{file_size},CHUNKS:{num_chunks}\n".encode()
        self.lora.send(header)

        for i in range(num_chunks):
            chunk_data = data[i * chunk_size: (i + 1) * chunk_size]
            chunk_header = f"CHUNK:{i + 1}/{num_chunks}\n".encode()
            self.lora.send(chunk_header + chunk_data)
            time.sleep(0.1)  # Short delay between chunks to prevent buffer overrun

        self.lora.send(b'END_OF_FILE')
        print("Data sent.")

    def receive_data(self, timeout=300, save_path=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        header_received = False
        file_size = 0
        num_chunks = 0
        filename = ""
        chunk_map = []
        transmission_ended = False

        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                print(f"Received data chunk: {data}")

                if not header_received:
                    if b'\n' in data:
                        header, data = data.split(b'\n', 1)
                        header = header.decode()
                        if "FILENAME:" in header and "SIZE:" in header and "CHUNKS:" in header:
                            header_received = True
                            filename = header.split("FILENAME:")[1].split(",")[0]
                            file_size = int(header.split("SIZE:")[1].split(",")[0])
                            num_chunks = int(header.split("CHUNKS:")[1])
                            chunk_map = [False] * num_chunks
                            print(f"Receiving file: {filename} of size {file_size} bytes in {num_chunks} chunks")
                if header_received and b'END_OF_FILE' in data:
                    transmission_ended = True
                    print("End of transmission detected.")
                    break

                if header_received:
                    while b'CHUNK:' in data:
                        chunk_header, data = data.split(b'\n', 1)
                        chunk_header = chunk_header.decode()
                        chunk_num = int(chunk_header.split("CHUNK:")[1].split("/")[0]) - 1
                        chunk_map[chunk_num] = True
                        received_data.extend(data[:chunk_size])
                        data = data[chunk_size:]

            if transmission_ended:
                break
            time.sleep(0.1)

        if transmission_ended and save_path:
            received_data = received_data[:file_size]  # Trim any extra data beyond the expected file size
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