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
        file_hash = hashlib.sha256(data).hexdigest()
        header = f"FILENAME:{filename},SIZE:{file_size},HASH:{file_hash}\n".encode()
        chunk_size = 240

        num_chunks = (file_size // chunk_size) + (1 if file_size % chunk_size != 0 else 0)
        for i in range(num_chunks):
            chunk = data[i*chunk_size:(i+1)*chunk_size]
            sequence_number = f"{i}/{num_chunks-1}".encode()
            self.lora.send(header + sequence_number + b':' + chunk + b'END_OF_FILE')
            time.sleep(1)  # Short delay between sending chunks
        print("Data sent.")

    def receive_data(self, timeout=300, save_path=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        header_received = False
        file_size = 0
        file_hash = ""
        filename = ""
        transmission_ended = False
        total_received_size = 0
        chunks = {}

        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                print(f"Received data chunk: {data}")

                if not header_received:
                    if b'\n' in data:
                        header, data = data.split(b'\n', 1)
                        header = header.decode()
                        if "FILENAME:" in header and "SIZE:" in header and "HASH:" in header:
                            header_received = True
                            filename = header.split("FILENAME:")[1].split(",")[0]
                            file_size = int(header.split("SIZE:")[1].split(",")[0])
                            file_hash = header.split("HASH:")[1]
                            print(f"Receiving file: {filename} of size {file_size} bytes with hash {file_hash}")

                if header_received:
                    sequence_number, chunk = data.split(b':', 1)
                    sequence_number = sequence_number.decode().split('/')
                    chunk_index = int(sequence_number[0])
                    total_chunks = int(sequence_number[1])
                    chunks[chunk_index] = chunk

                    if b'END_OF_FILE' in chunk:
                        chunk = chunk.replace(b'END_OF_FILE', b'')
                        transmission_ended = True
                        print("End of transmission detected.")
                        break

                    if len(chunks) == (total_chunks + 1):
                        transmission_ended = True
                        print("All chunks received.")
                        break

            time.sleep(0.1)

        if transmission_ended:
            received_data = b''.join([chunks[i] for i in sorted(chunks)])
            calculated_hash = hashlib.sha256(received_data).hexdigest()
            if calculated_hash == file_hash:
                if save_path:
                    with open(save_path, 'wb') as file:
                        file.write(received_data)
                        print(f"Data successfully saved to '{save_path}'")
                else:
                    save_path = f'/home/images/{filename}'
                    with open(save_path, 'wb') as file:
                        file.write(received_data)
                        print(f"Data successfully saved to '{save_path}'")
                print("File hash validation successful.")
            else:
                print("File hash validation failed.")
        else:
            print("Timeout reached without detecting end of transmission.")

        return bytes(received_data)