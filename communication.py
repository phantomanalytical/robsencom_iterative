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
        # Pack the metadata (file size and filename) into the start of the data
        metadata = struct.pack('<I', file_size) + filename.encode('utf-8') + b'\x00'
        data_with_metadata = metadata + data + b'END'
        self.lora.send(data_with_metadata)
        print("Data sent.")

    def receive_data(self, timeout=300, save_dir='/home/images/'):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        transmission_ended = False

        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                received_data += data
                print(f"Received data chunk: {data}")

                if b'END' in received_data:
                    print("End of transmission detected.")
                    received_data = received_data.split(b'END')[0]
                    transmission_ended = True
                    break
            time.sleep(0.1)

        if transmission_ended:
            # Extract metadata from the beginning of the received data
            file_size = struct.unpack('<I', received_data[:4])[0]
            filename = received_data[4:].split(b'\x00')[0].decode('utf-8')
            file_data = received_data[4 + len(filename) + 1:]  # +1 for null terminator

            if len(file_data) == file_size:
                save_path = save_dir + filename
                with open(save_path, 'wb') as file:
                    file.write(file_data)
                    print(f"Data successfully saved to '{save_path}'")
            else:
                print("File size mismatch. Data might be incomplete or corrupted.")
        else:
            print("Timeout reached without detecting end of transmission.")

        return bytes(received_data)
