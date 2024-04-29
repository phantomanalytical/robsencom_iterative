from sx126x import sx126x
import time

class LoRaComm:
    def __init__(self, address=36, serial_num='/dev/ttyS0', freq=915, power=22, rssi=False, air_speed=2400, buffer_size=240):
        # Convert address to integer if it's not already
        address = int(address) if isinstance(address, str) else address
        # Initialize the sx126x object with all necessary parameters
        self.lora = sx126x(serial_num=serial_num, freq=freq, addr=address, power=power, rssi=rssi, air_speed=air_speed, buffer_size=buffer_size)

    def update_address(self, new_address):
        # Dynamically update the address
        self.lora.update_address(new_address)

    def send_data(self, data):
        # Send data in packets if needed
        max_packet_size = 240  # This should match the largest packet size your module can handle; adjust as needed
        packets = [data[i:i + max_packet_size] for i in range(0, len(data), max_packet_size)]

        for packet in packets:
            if not self.lora.send(packet):
                print("Failed to send packet, retrying...")
                if not self.lora.send(packet):
                    print("Retry failed. Packet lost. Check device connectivity or settings.")
                    return False
        return True

    def receive_data(self, timeout=120):
        # Receive data with timeout handling
        data = self.lora.receive(timeout=timeout)
        if data:
            print("Data received successfully.")
        else:
            print("No data received within the timeout period.")
        return data

