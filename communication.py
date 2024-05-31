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
        chunk_size = 240
        num_chunks = len(data) // chunk_size + (1 if len(data) % chunk_size != 0 else 0)
        header = f"FILENAME:{filename},SIZE:{len(data)},CHUNKS:{num_chunks}\n".encode('utf-8')
        self.lora.send(header)
        for i in range(num_chunks):
            chunk = data[i * chunk_size:(i + 1) * chunk_size]
            sequence_number = i.to_bytes(4, byteorder='big')
            self.lora.send(sequence_number + chunk)  # Add sequence number to the chunk
            time.sleep(0.1)  # Small delay to allow the receiver to process chunks
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
        transmission_ended = False
        chunks = []

        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                print(f"Received data chunk: {data}")

                if not header_received:
                    received_data += data
                    if b'\n' in received_data:
                        header, received_data = received_data.split(b'\n', 1)
                        header = header.decode('utf-8')
                        if "FILENAME:" in header and "SIZE:" in header and "CHUNKS:" in header:
                            header_received = True
                            filename = header.split("FILENAME:")[1].split(",")[0]
                            file_size = int(header.split("SIZE:")[1].split(",")[0])
                            num_chunks = int(header.split("CHUNKS:")[1])
                            print(f"Receiving file: {filename} of size {file_size} bytes in {num_chunks} chunks")
                            chunks = [b''] * num_chunks

                if header_received:
                    try:
                        sequence_number = int.from_bytes(data[:4], byteorder='big')  # Extract sequence number
                        chunk_data = data[4:]  # Extract actual chunk data
                        chunks[sequence_number] = chunk_data  # Store chunk in its correct position
                        if b'END_OF_FILE' in received_data:
                            transmission_ended = True
                            print("End of transmission detected.")
                            break
                    except ValueError as e:
                        print(f"Error decoding sequence number: {e}")

            time.sleep(0.1)

        if transmission_ended:
            received_data = b''.join(chunks)
            received_data = received_data.replace(b'\r', b'').replace(b'\n', b'')  # Remove new lines
            if save_path:
                with open(save_path, 'wb') as file:
                    file.write(received_data)
                    print(f"Data successfully saved to '{save_path}'")
            else:
                save_path = f'/home/images/{filename}'
                with open(save_path, 'wb') as file:
                    file.write(received_data)
                    print(f"Data successfully saved to '{save_path}'")

            # Verify file size
            if len(received_data) == file_size:
                print("File received successfully and file size matches.")
            else:
                print("File size mismatch.")
        else:
            print("Timeout reached without detecting end of transmission.")

        return bytes(received_data)