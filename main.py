import csv
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

    start_time = time.time()
    lora_comm.send_data(open(file_path, 'rb').read())
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
    address = int(user_input("Enter the LoRa address: "))
    lora_comm = LoRaComm(address=address)

    choice = user_input("Would you like to send or receive a file? (send/receive): ", ['send', 'receive'])
    if choice == 'send':
        file_path = user_input("Enter the path to the image file: ")
        if user_input("Iterate through power settings? (yes/no): ", ['yes', 'no']) == 'yes':
            power_settings = [22, 17, 13, 10]  # Define power settings
            results = iterative_test(lora_comm, file_path, 'power', power_settings)
            save_results(results, 'power')

        if user_input("Iterate through air speed settings? (yes/no): ", ['yes', 'no']) == 'yes':
            air_speeds = [1200, 2400, 4800, 9600]  # Define air speeds
            results = iterative_test(lora_comm, file_path, 'air_speed', air_speeds)
            save_results(results, 'air_speed')
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
