from sx126x import sx126x

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
        success = self.lora.send(data)
        if not success:
            print("Data transmission failed.")
            return False
        return True

    def receive_data(self, timeout=120):
        data = self.lora.receive(timeout=timeout)
        if data is None:
            print("No data received or incomplete data.")
            return None
        return data

