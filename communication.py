from sx126x import sx126x
import time

class LoRaComm:
    def __init__(self, address=36, serial_num='/dev/ttyS0', freq=915, power=22, rssi=False, air_speed=2400):
        self.lora = sx126x(serial_num=serial_num, freq=freq, addr=address, power=power, rssi=rssi, air_speed=air_speed)

    def update_settings(self, power=None, air_speed=None):
        if power is not None and air_speed is not None:
            self.lora.update_module_settings(power=power, air_speed=air_speed)
        elif power is not None:
            self.lora.update_module_settings(power=power)
        elif air_speed is not None:
            self.lora.update_module_settings(air_speed=air_speed)

    def send_data(self, data):
        if isinstance(data, str):
            data = data.encode()  # Convert string to bytes if necessary
        success = self.lora.send(data)
        if not success:
            print("Data transmission failed. No ACK received.")
            return False
        return True

    def receive_data(self, timeout=120, save_file=False, setting_type=None, iteration_number=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        while True:
            if self.lora.ser.in_waiting:
                new_data = self.lora.ser.read(self.lora.ser.in_waiting)
                received_data += new_data
                print(f"Received data chunk: {new_data}")

                # Handle test message
                if b'transmit' in received_data:
                    self.send_data(b'success')
                    print("Test message received. Sent ACK 'success'.")
                    continue  # Continue to listen after a test message

                # Break if end of transmission marker is found
                if b'END' in received_data:
                    self.lora.ser.write(b'ACK')
                    print("End of data transmission detected. Sent ACK.")
                    break

            if time.time() - start_time > timeout:
                print("Timeout reached while waiting for data.")
                break
            time.sleep(0.1)

        # Save data to a file if not a test and if needed
        if save_file and received_data and not b'transmit' in received_data:
            file_path = f'image_{iteration_number}_{setting_type}.png'
            with open(file_path, 'wb') as file:
                file.write(received_data)
                print(f"Data successfully saved to '{file_path}'.")

        return bytes(received_data)

