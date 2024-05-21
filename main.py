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

def main():
    print("Starting main function...")
    try:
        address = int(user_input("Enter the LoRa address: "))
        lora_comm = LoRaComm(address=address, serial_num='/dev/serial0', freq=915, power=22, rssi=False, air_speed=2400)

        choice = user_input("Would you like to send or receive a file? (send/receive): ", ['send', 'receive'])
        if choice == 'send':
            file_path = user_input("Enter the path to the image file: ")
            while True:
                setting_type = user_input("Choose setting to iterate (p for power, s for spreading factor, q to quit): ", ['p', 's', 'q'])
                if setting_type == 'q':
                    break
                if setting_type == 'p':
                    power_settings = [22, 17, 13, 10]
                    results = iterative_test(lora_comm, file_path, 'power', power_settings)
                    save_results(results, 'power')
                elif setting_type == 's':
                    air_speeds = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
                    results = iterative_test(lora_comm, file_path, 'air_speed', air_speeds)
                    save_results(results, 'air_speed')
        elif choice == 'receive':
            print("Device set to receive mode.")
            setting_type = user_input("Enter setting type for received files (e.g., 'power', 'air_speed'): ")
            settings_count = {'power': 4, 'air_speed': 8}  # Settings count
            i = 0
            while i < settings_count.get(setting_type, 4):  # Default to 4 if type is not found
                save_file_path = f'/home/pi/image_{i+1}_{setting_type}.png'
                data = lora_comm.receive_data(save_path=save_file_path)
                if data:
                    print(f"Data received and saved as {save_file_path}.")
                    i += 1
                    continue_choice = user_input("Continue receiving? (yes/no): ", ['yes', 'no'])
                    if continue_choice == 'no':
                        break
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    print("Main function completed.")
