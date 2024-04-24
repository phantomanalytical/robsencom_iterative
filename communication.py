from sx126x import sx126x
import time

class LoRaComm:
    def __init__(self, address=36, serial_num='/dev/ttyS0', freq=915, power=22, rssi=False):
        # Convert address to integer if it's not already
        address = int(address) if isinstance(address, str) else address
        self.lora = sx126x(serial_num=serial_num, freq=freq, addr=address, power=power, rssi=rssi)

    def send_data(self, data):
        self.lora.send(data)

    def receive_data(self, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            data = self.lora.receive()
            if data:
                return data
        return None

