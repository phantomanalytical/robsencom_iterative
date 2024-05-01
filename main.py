import csv
import os
import time
from communication import LoRaComm

def user_input(prompt, options=None):
    """ Helper function to handle user input and validate it against provided options. """
    user_choice = input(prompt)
    while options and user_choice.lower().strip() not in options:
        print("Invalid option. Please try again.")
        user_choice = input(prompt)
    return user_choice

def perform_test_transmission(lora_comm):
    """ Sends a test message and expects a specific reply. """
    print("Sending test message...")
    if lora_comm.send_data(b"transmit"):
        response = lora_comm.receive_data(timeout=15)
        if response == b"success":
            print("Test successful, proceeding with settings iteration.")
            return True
    print("Test failed, no correct response received.")
    return False

def perform_transmission(lora_comm, setting_type, setting_value, file_path):
    """ Send an image file with specific settings and measure latency. """
    if setting_type == 'power':
        lora_comm.update_settings(power=setting_value)
    elif setting_type == 'air_speed':
        lora_comm.update_settings(air_speed=setting_value)

    with open(file_path, 'rb') as file:
        data = file.read()

    start_time = time.time()
    lora_comm.send_data(data)
    latency = time.time() - start_time
    return latency

def iterative_test(lora_comm, file_path, setting_type, values):
    """ Iteratively tests different settings and save transmitted images with naming convention. """
    results = []
    for i, value in enumerate(values):
        latency = perform_transmission(lora_comm, setting_type, value, file_path)
        results.append([value, latency])
        print(f"Tested {setting_type} {value} with latency {latency} seconds.")
        save_file_path = f'image_{i + 1}_{setting_type}.png'
        lora_comm.receive_data(save_path=save_file_path)
    return results

def save_results(results, setting_type):
    """ Saves the test results into a CSV file. """
    filename = f"{setting_type}_results.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Setting Value', 'Latency'])
        for result in results:
            writer.writerow(result)
    print(f"Results saved to {filename}.")

def main():
    print("Starting main function...")
    try:
        address = int(user_input("Enter the LoRa address: "))
        lora_comm = LoRaComm(address=address, serial_num='/dev/ttyS0', freq=915, power=22, rssi=False, air_speed=2400)

        choice = user_input("Would you like to send or receive a file? (send/receive): ", ['send', 'receive'])
        if choice == 'send':
            if perform_test_transmission(lora_comm):
                file_path = user_input("Enter the path to the image file: ")
                if user_input("Iterate through power settings? (yes/no): ", ['yes', 'no']) == 'yes':
                    power_settings = [22, 17, 13, 10]
                    results = iterative_test(lora_comm, file_path, 'power', power_settings)
                    save_results(results, 'power')
                if user_input("Iterate through air speed settings? (yes/no): ", ['yes', 'no']) == 'yes':
                    air_speeds = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
                    results = iterative_test(lora_comm, file_path, 'air_speed', air_speeds)
                    save_results(results, 'air_speed')
        elif choice == 'receive':
            print("Device set to receive mode.")
            while True:
                data = lora_comm.receive_data()
                if data:
                    if data == b'transmit':
                        print("Test message received. Sending ACK 'success'.")
                        lora_comm.send_data(b'success', wait_for_ack=True)  # Corrected to wait_for_ack
                    else:
                        print("Data received.")
                        with open('received_image.png', 'wb') as file:
                            file.write(data)
                        print("Image saved to 'received_image.png'.")
                        break
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    print("Main function completed.")

