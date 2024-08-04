import json
import os
from datetime import datetime

def load_state_abbreviations(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data['states']

def create_files_for_states(state_abbreviations):
    today = datetime.today().strftime('%m%d%y')
    for state in state_abbreviations:
        filename = f"MS_{today}_{state}.txt"
        with open(filename, 'w') as file:
            file.write(f"File for {state}")

def main():
    json_file = 'states.json'
    state_abbreviations = load_state_abbreviations(json_file)
    create_files_for_states(state_abbreviations)

if __name__ == "__main__":
    main()
