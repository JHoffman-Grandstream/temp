import requests
import os
import json
import time
import urllib.parse

def load_existing_cards(json_file_path):
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            return json.load(file)
    return {}

def save_card_to_json(json_file_path, card_data):
    with open(json_file_path, 'w') as file:
        json.dump(card_data, file, indent=4)

def query_scryfall(card_name, max_retries=3):
    """
    Query the Scryfall API for a given card name with retry mechanism.
    Returns the card data.
    """
    encoded_card_name = urllib.parse.quote(card_name)  # Encode special characters like '&'
    url = f"https://api.scryfall.com/cards/named?exact={encoded_card_name}"
    retry_interval = 1  # start with 1 second

    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Non-200 response for {card_name} on attempt {attempt + 1} - Request URL: {url}")
        except requests.RequestException as e:
            print(f"Error on attempt {attempt + 1} for {card_name}: {e} - Request URL: {url}")

        time.sleep(retry_interval)
        retry_interval *= 2  # double the interval for each retry

    print(f"Failed to retrieve {card_name} after {max_retries} attempts - Request URL: {url}")
    return None

def convert_dck_to_json_format(dck_file_path):
    """
    Converts a .dck file to a JSON format.
    """
    converted_cards = []

    with open(dck_file_path, 'r') as file:
        for line in file:
            if '|' in line and line[0].isdigit():
                _, card_info = line.split(' ', 1)
                card_name = card_info.split('|')[0].strip()
                card_data = query_scryfall(card_name)
                if card_data:
                    converted_cards.append(card_data)

    return converted_cards

def process_dck_files_in_directory(folder_path):
    all_cards = load_existing_cards(os.path.join(folder_path, 'all_cards.json'))

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.dck'):
                dck_file_path = os.path.join(root, filename)
                with open(dck_file_path, 'r') as file:
                    for line in file:
                        if '|' in line and line[0].isdigit():
                            _, card_info = line.split(' ', 1)
                            card_name = card_info.split('|')[0].strip()

                            if card_name not in all_cards:
                                card_data = query_scryfall(card_name)
                                if card_data:
                                    all_cards[card_name] = card_data
                                    save_card_to_json(os.path.join(folder_path, 'all_cards.json'), all_cards)

    print(f"All cards have been processed and saved to 'all_cards.json'.")


# Example usage for a folder containing .dck files
folder_path = 'C:\\Users\\jhoff\\OneDrive\\Documents\\temp\\decks'
process_dck_files_in_directory(folder_path)
