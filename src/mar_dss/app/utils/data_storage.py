import json
import pandas as pd
# Global data storage dictionary
_data_storage = {}

def get_data(key):
    """Get the global data storage dictionary"""
    return _data_storage

def set_data(key, value):
    """Add data to the global storage"""
    _data_storage[key] = value

def to_json():
    """Save data to a json file"""
    with open("data.json", "w") as f:
        json.dump(_data_storage, f)

def from_json():
    """Load data from a json file"""
    with open("data.json", "r") as f:
        _data_storage = json.load(f)

def from_csv():
    """Load data from a csv file"""
    with open("data.csv", "r") as f:
        _data_storage = pd.read_csv(f)
        # convert to dictionary
        _data_storage = _data_storage.to_dict(orient="records")

def to_csv():
    """Save data to a csv file"""
    with open("data.csv", "w") as f:
        pd.DataFrame(_data_storage).to_csv(f, index=False)


def clear_data():
    """Clear all data from storage"""
    global _data_storage
    _data_storage.clear()

def get_data_storage():
    """Get the entire data storage dictionary"""
    return _data_storage
