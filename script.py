import requests
import os
import json

def query_scryfall(card_name):
    """
    Query the Scryfall API for a given card name.
    Returns the card data.
    """
    url = f"https://api.scryfall.com/cards/named?exact={card_name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            card_info = response.json()
            return {
                'name': card_info['name'],
                'type': card_info['type_line'],
                'manaCost': card_info.get('mana_cost', ''),
                'rarity': card_info.get('rarity', ''),
                'setCode': card_info.get('set', ''),
                'text': card_info.get('oracle_text', ''),
                'power': card_info.get('power', ''),
                'toughness': card_info.get('toughness', '')
            }
    except requests.RequestException as e:
        print(f"Error querying Scryfall API for {card_name}: {e}")
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
    """
    Processes all .dck files in a given directory and its subdirectories,
    and collates all cards into one big JSON file.
    """
    all_cards = []

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.dck'):
                dck_file_path = os.path.join(root, filename)
                converted_deck = convert_dck_to_json_format(dck_file_path)
                all_cards.extend(converted_deck)

    # Save all collected cards to a single JSON file
    json_file_path = os.path.join(folder_path, 'all_cards.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(all_cards, json_file, indent=4)

    print(f"All cards have been processed and saved to 'all_cards.json'.")

# Example usage for a folder containing .dck files
folder_path = 'C:\\Users\\jhoff\\OneDrive\\Documents\\temp\\decks'
process_dck_files_in_directory(folder_path)
