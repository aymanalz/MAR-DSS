import json
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
