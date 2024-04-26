import csv
import os
import time
from communication import LoRaComm
from file_manager import get_file_info, compress_file, decompress_file

def user_input(prompt, options=None):
    """ Helper function to handle user input and validate it against provided options. """
    user_choice = input(prompt)
    while options and user_choice.lower().strip() not in options:
        print("Invalid option. Please try again.")
        user_choice = input(prompt)
    return user_choice

def set_device_settings(lora_comm, address):
    """ Sets the initial LoRa device settings using the provided address. """
    lora_comm.lora.set(
        freq=lora_comm.lora.freq,
        addr=address,
        power=lora_comm.lora.power,
        rssi=lora_comm.lora.rssi,
        air_speed=lora_comm.lora.air_speed,
        net_id=0,
        buffer_size=240,
        crypt=0,
        relay=False,
        lbt=False,
        wor=False
    )

def perform_transmission(lora_comm, power, spreading_factor, file_path):
    """ Send an image file with specific power and spreading factor, and measure latency. """
    lora_comm.lora.set(
        freq=lora_comm.lora.freq,
        addr=lora_comm.lora.addr,
        power=power,
        rssi=lora_comm.lora.rssi,
        air_speed=spreading_factor,
        net_id=0,
        buffer_size=240,
        crypt=0,
        relay=False,
        lbt=False,
        wor=False
    )
    start_time = time.time()
    lora_comm.send_data(open(file_path, 'rb').read())
    latency = time.time() - start_time
    return latency

def iterative_test(lora_comm, file_path, parameter, values):
    """ Iteratively tests different power or spreading factor settings. """
    results = []
    fixed_value = 2400 if parameter == 'power' else 22  # Default values
    for value in values:
        if parameter == 'power':
            latency = perform_transmission(lora_comm, value, fixed_value, file_path)
        else:  # spreading_factor
            latency = perform_transmission(lora_comm, fixed_value, value, file_path)
        results.append([value, fixed_value, latency])
        print(f"Tested {parameter} {value} with latency {latency} seconds.")
    return results

def save_results(results, parameter):
    """ Saves the test results into a CSV file. """
    filename = f"{parameter}_results.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Setting', 'Fixed Value', 'Latency'])
        for result in results:
            writer.writerow(result)
    print(f"Results saved to {filename}.")

def main():
    address = int(user_input("Enter the LoRa address: "))
    lora_comm = LoRaComm(address=address)  # Adjusted for direct initialization with address

    set_device_settings(lora_comm, address)  # Apply initial settings

    choice = user_input("Would you like to send or receive a file? (send/receive): ", ['send', 'receive'])
    if choice == 'send':
        file_path = user_input("Enter the path to the image file: ")
        _, file_size = get_file_info(file_path)  # Assumes get_file_info returns path and file size

        if user_input("Iterate through power settings? (yes/no): ", ['yes', 'no']) == 'yes':
            power_settings = [22, 17, 13, 10]  # Define your power settings
            results = iterative_test(lora_comm, file_path, 'power', power_settings)
            save_results(results, 'power')

        if user_input("Iterate through spreading factor settings? (yes/no): ", ['yes', 'no']) == 'yes':
            spreading_factors = [1200, 2400, 4800, 9600]  # Define your spreading factors
            results = iterative_test(lora_comm, file_path, 'spreading_factor', spreading_factors)
            save_results(results, 'spreading_factor')
    elif choice == 'receive':
        print("Device set to receive mode.")
        while True:
            data = lora_comm.receive_data()
            if data:
                print("Data received.")
                break
            else:
                if user_input("No data received. Would you like to remain in receive mode? (yes/no): ", ['yes', 'no']) == 'no':
                    break

if __name__ == "__main__":
    main()
