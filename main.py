import csv
import os
import time  # Ensure the time module is imported
from communication import LoRaComm

def user_input(prompt, options=None):
    """ Helper function to handle user input and validate it against provided options. """
    user_choice = input(prompt)
    while options and user_choice.lower().strip() not in options:
        print("Invalid option. Please try again.")
        user_choice = input(prompt)
    return user_choice

def perform_test_transmission(lora_comm):
    """ Sends a test message and expects a specific reply to ensure the communication link is working. """
    print("Sending test message...")
    lora_comm.send_data("transmit".encode())  # Encoding the string to bytes
    response = lora_comm.receive_data(timeout=15)
    if response and response.decode() == "success":  # Decoding the received bytes to string
        print("Test successful, proceeding with power settings.")
        return True
    else:
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
    """ Iteratively tests different settings. """
    results = []
    for value in values:
        latency = perform_transmission(lora_comm, setting_type, value, file_path)
        results.append([value, latency])
        print(f"Tested {setting_type} {value} with latency {latency} seconds.")
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
        print(f"Address entered: {address}")
        lora_comm = LoRaComm(address=address, serial_num='/dev/ttyS0', freq=915, power=22, rssi=False, air_speed=2400)
        print("LoRa communication initialized.")

        choice = user_input("Would you like to send or receive a file? (send/receive): ", ['send', 'receive'])
        print(f"Choice selected: {choice}")
        if choice == 'send':
            if perform_test_transmission(lora_comm):  # Ensure the transmission test is only performed if sending
                file_path = user_input("Enter the path to the image file: ")
                if user_input("Iterate through power settings? (yes/no): ", ['yes', 'no']) == 'yes':
                    power_settings = [22, 17, 13, 10]  # Define power settings
                    results = iterative_test(lora_comm, file_path, 'power', power_settings)
                    save_results(results, 'power')

                if user_input("Iterate through air speed settings? (yes/no): ", ['yes', 'no']) == 'yes':
                    air_speeds = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]  # Define air speeds
                    results = iterative_test(lora_comm, file_path, 'air_speed', air_speeds)
                    save_results(results, 'air_speed')
        elif choice == 'receive':
            print("Device set to receive mode.")
            while True:
                data = lora_comm.receive_data()
                if data:
                    if data == b'transmit':
                        print("Test message received.")
                        lora_comm.send_data(b'success')  # Responding to the test message
                        print("Response sent back.")
                    else:
                        print("Data received.")
                        # Save received data to a PNG file if it's actual data
                        with open('received_image.png', 'wb') as file:
                            file.write(data)
                        print("Image saved to 'received_image.png'.")
                        break
                else:
                    if user_input("No data received. Would you like to remain in receive mode? (yes/no): ", ['yes', 'no']) == 'no':
                        break
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    print("Main function completed.")
