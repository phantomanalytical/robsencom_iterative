from sx126x import sx126x
import time

class LoRaComm:
    def __init__(self, address=36, serial_num='/dev/ttyACM0', power=22, spreading_factor=7, coding_rate=1, network_id=0):
        self.lora = sx126x(serial_num=serial_num, address=address, power=power, spreading_factor=spreading_factor, coding_rate=coding_rate, network_id=network_id)

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

    def send_data(self, data):
        print("Attempting to send data...")
        # Append the 'END' marker to the data
        data += b'END'
        self.lora.send(data)
        print("Data sent.")

    def receive_data(self, timeout=300, save_path=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        transmission_ended = False

        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                received_data += data
                print(f"Received data chunk: {data}")

                # Check for an 'END' marker indicating the end of a transmission
                if b'END' in received_data:
                    print("End of transmission detected.")
                    received_data = received_data.split(b'END')[0]  # Remove the 'END' marker before processing
                    transmission_ended = True
                    break

            if transmission_ended:
                break
            time.sleep(0.1)

        if save_path and received_data:
            with open(save_path, 'wb') as file:
                file.write(received_data)
                print(f"Data successfully saved to '{save_path}'")

        if not transmission_ended:
            print("Timeout reached without detecting end of transmission.")

        return bytes(received_data)