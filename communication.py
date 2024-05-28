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

        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            self.lora.send(header + chunk + b'END_OF_FILE')
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

        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                received_data += data
                print(f"Received data chunk: {data}")

                if not header_received:
                    if b'\n' in received_data:
                        header, received_data = received_data.split(b'\n', 1)
                        header = header.decode()
                        if "FILENAME:" in header and "SIZE:" in header and "HASH:" in header:
                            header_received = True
                            filename = header.split("FILENAME:")[1].split(",")[0]
                            file_size = int(header.split("SIZE:")[1].split(",")[0])
                            file_hash = header.split("HASH:")[1]
                            print(f"Receiving file: {filename} of size {file_size} bytes with hash {file_hash}")

                if header_received:
                    if b'END_OF_FILE' in received_data:
                        received_data = received_data.replace(b'END_OF_FILE', b'')
                        total_received_size += len(received_data)
                        if total_received_size >= file_size:
                            transmission_ended = True
                            print("End of transmission detected.")
                            break

            time.sleep(0.1)

        if transmission_ended:
            # Remove any extra characters that might have been included
            received_data = received_data.replace(b'\r', b'').replace(b'\n', b'')
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