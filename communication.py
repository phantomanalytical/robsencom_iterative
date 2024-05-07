from sx126x import sx126x
import time

class LoRaComm:
    def __init__(self, address=36, serial_num='/dev/ttyS0', freq=915, power=22, rssi=False, air_speed=2400):
        self.lora = sx126x(serial_num=serial_num, freq=freq, addr=address, power=power, rssi=rssi, air_speed=air_speed)

    def update_settings(self, power=None, air_speed=None):
        if power is not None:
            self.lora.update_module_settings(power=power)
        if air_speed is not None:
            self.lora.update_module_settings(air_speed=air_speed)

    def send_data(self, data):
        print("Attempting to send data...")
        self.lora.send(data)  # Send data

    def receive_data(self, timeout=120, save_path=None):
        print("Waiting to receive data...")
        received_data = self.lora.receive(timeout=timeout)

        if received_data and save_path:
            with open(save_path, 'wb') as file:
                file.write(received_data)
                print(f"Data successfully saved to '{save_path}'")
        else:
            print("No data received or data incomplete.")

        return received_data
