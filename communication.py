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
        chunk_size = 240  # Define chunk size
        num_chunks = len(data) // chunk_size + (1 if len(data) % chunk_size != 0 else 0)
        header = f"FILENAME:{filename},SIZE:{len(data)},CHUNKS:{num_chunks}\n".encode()

        # Send header
        self.lora.send(header)
        time.sleep(1)  # Small delay between sending header and data

        # Send data chunks
        for i in range(num_chunks):
            chunk = data[i * chunk_size:(i + 1) * chunk_size]
            packet = f"SEQ:{i + 1}/#{num_chunks}\n".encode() + chunk
            self.lora.send(packet)
            time.sleep(0.5)  # Small delay between sending chunks

        # Send end-of-file marker
        self.lora.send(b'END_OF_FILE')
        print("Data sent.")

    def receive_data(self, timeout=300, save_path=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        header_received = False
        num_chunks = 0
        received_chunks = []
        filename = ""
        file_size = 0

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
                            received_chunks = [None] * num_chunks
                            print(f"Receiving file: {filename} of size {file_size} bytes in {num_chunks} chunks")

                if header_received:
                    if b'END_OF_FILE' in data:
                        print("End of transmission detected.")
                        break

                    if b'\n' in data:
                        seq_info, chunk = data.split(b'\n', 1)
                        seq_info = seq_info.decode()
                        if "SEQ:" in seq_info:
                            seq_num = int(seq_info.split("SEQ:")[1].split("/")[0]) - 1
                            if 0 <= seq_num < num_chunks:
                                received_chunks[seq_num] = chunk

            time.sleep(0.1)

        received_data = b''.join(filter(None, received_chunks))

        if save_path:
            with open(save_path, 'wb') as file:
                file.write(received_data)
                print(f"Data successfully saved to '{save_path}'")
        else:
            save_path = f'/home/images/{filename}'
            with open(save_path, 'wb') as file:
                file.write(received_data)
                print(f"Data successfully saved to '{save_path}'")

        if not received_data:
            print("Timeout reached without detecting end of transmission or incomplete data received.")

        return bytes(received_data)
