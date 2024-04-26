from sx126x import sx126x
import time

class LoRaComm:
    def __init__(self, address=36, serial_num='/dev/ttyS0', freq=915, power=22, rssi=False):
        # Convert address to integer if it's not already
        address = int(address) if isinstance(address, str) else address
        self.lora = sx126x(serial_num=serial_num, freq=freq, addr=address, power=power, rssi=rssi)

    def update_address(self, new_address):
        self.lora.update_address(new_address)  # Dynamically update the address

    def send_data(self, data):
        success = self.lora.send(data)
        if not success:
            print("Failed to send data after retries. Check device connectivity or settings.")

    def receive_data(self, timeout=120):  # Increased timeout to accommodate larger data or delays
        start_time = time.time()
        while True:
            data = self.lora.receive()
            if data:
                return data
            if time.time() - start_time > timeout:
                break  # Exit if the timeout is reached
            time.sleep(0.1)  # Slight delay to allow data to accumulate in the input buffer
        return None

