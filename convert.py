import json

# Define a function to read and process the JSON file
def read_mtg_cards_from_json(filename):
    try:
        with open(filename, 'r') as json_file:
            card_data = json.load(json_file)
            for card in card_data:
                print("Name:", card["name"])
                print("Type:", card["type"])
                print("Mana Cost:", card["manaCost"])
                print("Rarity:", card["rarity"])
                print("Set Code:", card["setCode"])
                print("Text:", card["text"])
                print("Power:", card["power"])
                print("Toughness:", card["toughness"])
                print("\n")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{filename}'.")

# Specify the JSON file containing MTG card data
json_filename = "database.json"

# Call the function to read and process the JSON file
read_mtg_cards_from_json(json_filename)