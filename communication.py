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
        if self.lora.send(data):
            print("Data sent successfully.")
        else:
            print("Failed to send data.")

    def receive_data(self, timeout=120, save_path=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        while True:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                received_data += data
                print(f"Received data chunk: {data}")

            # Check for an 'END' marker indicating the end of a transmission
            if b'END' in received_data:
                print("End of transmission detected.")
                self.lora.ser.write(b'ACK')  # Send ACK after receiving complete data
                received_data = received_data.split(b'END')[0]  # Assume everything before 'END' is the message
                break

            if time.time() - start_time > timeout:
                print("Timeout reached while waiting for data.")
                break
            time.sleep(0.1)

        if save_path and received_data:
            with open(save_path, 'wb') as file:
                file.write(received_data)
                print(f"Data successfully saved to '{save_path}'")

        return bytes(received_data)

