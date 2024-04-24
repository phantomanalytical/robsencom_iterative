import pickle

def save_address():
    address = input("Enter the address number of your LoRa module: ")
    with open("module_address.pkl", "wb") as f:
        pickle.dump(address, f)
    return address

def load_address():
    try:
        with open("module_address.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None