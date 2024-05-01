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
        self.lora.send(data)  # Initial attempt to send data
        if not self.wait_for_ack():
            print("No ACK received. Retrying...")
            self.lora.send(data)  # Retry sending data
            if not self.wait_for_ack():
                print("Retry failed. Check connection.")
                return False
        return True

    def wait_for_ack(self):
        """ Wait for an ACK from the receiver. """
        start_time = time.time()
        timeout = 5  # seconds
        while time.time() - start_time < timeout:
            if self.lora.ser.in_waiting:
                ack = self.lora.ser.read(self.lora.ser.in_waiting)
                if ack == b'ACK':
                    return True
        return False

    def receive_data(self, timeout=120, save_path=None):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        while True:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                received_data += data
                print(f"Received data chunk: {data}")

            if b'END' in received_data:
                print("End of transmission detected.")
                self.lora.ser.write(b'ACK')
                break

            if time.time() - start_time > timeout:
                print("Timeout reached while waiting for data.")
                break
            time.sleep(0.1)

        if save_path:
            with open(save_path, 'wb') as file:
                file.write(received_data)
                print(f"Data successfully saved to '{save_path}'")
        return bytes(received_data)
