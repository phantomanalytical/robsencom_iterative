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
    for i, value in enumerate(values):
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

def settings_iteration(lora_comm):
    """ Handles settings iteration based on user choice. """
    continue_testing = True
    while continue_testing:
        choice = user_input("Would you like to iterate through power or air speed settings? (power/air_speed/quit): ", ['power', 'air_speed', 'quit'])
        if choice == 'quit':
            print("Exiting the program.")
            continue_testing = False
        else:
            file_path = user_input("Enter the path to the image file: ")
            if choice == 'power':
                power_settings = [22, 17, 13, 10]  # Define power settings
                results = iterative_test(lora_comm, file_path, 'power', power_settings)
                save_results(results, 'power')
            elif choice == 'air_speed':
                air_speeds = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]  # Define air speeds
                results = iterative_test(lora_comm, file_path, 'air_speed', air_speeds)
                save_results(results, 'air_speed')

def main():
    print("Starting main function...")
    try:
        address = int(user_input("Enter the LoRa address: "))
        lora_comm = LoRaComm(address=address, serial_num='/dev/ttyS0', freq=915, power=22, rssi=False, air_speed=2400)

        mode = user_input("Would you like to send or receive a file? (send/receive): ", ['send', 'receive'])
        if mode == 'send':
            settings_iteration(lora_comm)
        elif mode == 'receive':
            print("Device set to receive mode.")
            while True:
                data = lora_comm.receive_data()
                if data:
                    print("Data received and saved.")
                    break
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    print("Main function completed.")
