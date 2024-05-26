from sx126x import sx126x
import time

class LoRaComm:
    def __init__(self, address=36, serial_num='/dev/ttyACM0', freq=915, power=22, rssi=False, air_speed=2400):
        self.lora = sx126x(serial_num=serial_num, freq=freq, addr=address, power=power, rssi=rssi, air_speed=air_speed)

    def update_settings(self, power=None, air_speed=None):
        if power is not None:
            self.lora.update_module_settings(power=power)
        if air_speed is not None:
            self.lora.update_module_settings(air_speed=air_speed)

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
                if b'END' in received_content:
                    print("End of transmission detected.")
                    received_data = received_data[:-3]  # Assuming 'END' is at the very end and is 3 bytes long
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