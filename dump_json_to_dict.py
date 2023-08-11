
import json

# Open the JSON file
with open('part_number_config.json') as f:
    # Load the JSON content
    json_data_raw = json.load(f)

# Decode the JSON data to a Python dictionary
json_dict = json.loads(json.dumps(json_data_raw))

# Print the Python dictionary
print(json_dict)

