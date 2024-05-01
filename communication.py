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
        print(f"Attempting to send data: {data}")
        if not self.lora.send(data):
            print("No ACK received. Retrying...")
            if not self.lora.send(data):
                print("Retry failed. Check connection.")
                return False
        return True

    def receive_data(self, timeout=120):
        print("Waiting to receive data...")
        start_time = time.time()
        received_data = bytearray()
        while True:
            if self.lora.ser.in_waiting:
                data = self.lora.ser.read(self.lora.ser.in_waiting)
                received_data += data
                print(f"Received data chunk: {data}")
                
                # Handle specific protocol messages
                if b'transmit' in received_data:
                    print("Test message 'transmit' received.")
                    self.send_data(b'success')
                    received_data.clear()  # Clear buffer after handling
                if b'END' in received_data:
                    print("End of transmission detected.")
                    break

            if time.time() - start_time > timeout:
                print("Timeout reached while waiting for data.")
                break
            time.sleep(0.1)
        return bytes(received_data)
