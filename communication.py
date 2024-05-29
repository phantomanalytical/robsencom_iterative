from sx126x import sx126x
import time
import struct

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
        header = f"FILENAME:{filename},SIZE:{file_size},CHUNKS:{(file_size + chunk_size - 1) // chunk_size}\n".encode('utf-8')
        self.lora.send(header)
        for i in range(0, file_size, chunk_size):
            chunk = data[i:i + chunk_size]
            sequence_number = i // chunk_size
            packet = struct.pack('>I', sequence_number) + chunk
            self.lora.send(packet)
        self.lora.send(b'END_OF_FILE')
        print("Data sent.")

    def receive_data(self, timeout=300, save_path=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        header_received = False
        file_size = 0
        filename = ""
        total_chunks = 0
        received_chunks = []
        transmission_ended = False

        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                if not header_received:
                    if b'\n' in data:
                        header, data = data.split(b'\n', 1)
                        header = header.decode('utf-8')
                        if "FILENAME:" in header and "SIZE:" in header and "CHUNKS:" in header:
                            header_received = True
                            filename = header.split("FILENAME:")[1].split(",")[0]
                            file_size = int(header.split("SIZE:")[1].split(",")[0])
                            total_chunks = int(header.split("CHUNKS:")[1])
                            received_chunks = [None] * total_chunks
                            print(f"Receiving file: {filename} of size {file_size} bytes in {total_chunks} chunks")
                
                if header_received:
                    if b'END_OF_FILE' in data:
                        transmission_ended = True
                        print("End of transmission detected.")
                        break
                    if len(data) > 4:
                        seq_number = struct.unpack('>I', data[:4])[0]
                        chunk = data[4:]
                        received_chunks[seq_number] = chunk

            time.sleep(0.1)

        if transmission_ended:
            received_data = b''.join(chunk for chunk in received_chunks if chunk)
            if save_path:
                with open(save_path, 'wb') as file:
                    file.write(received_data)
                    print(f"Data successfully saved to '{save_path}'")
            else:
                save_path = f'/home/images/{filename}'
                with open(save_path, 'wb') as file:
                    file.write(received_data)
                    print(f"Data successfully saved to '{save_path}'")

        if not transmission_ended:
            print("Timeout reached without detecting end of transmission.")

        return bytes(received_data)