import json

def convert_to_new_format(input_file, output_file):
    # Load the existing cards from the input JSON file
    with open(input_file, 'r') as file:
        existing_cards = json.load(file)

    # Create a list to store the cards in the new format
    new_format_cards = []

    for card_name, card_data in existing_cards.items():
        # Extract relevant information from card_data
        card_type = card_data.get("type_line", "")
        mana_cost = card_data.get("mana_cost", "")
        rarity = card_data.get("rarity", "")
        set_code = card_data.get("setCode", "")
        text = card_data.get("oracle_text", "")
        power = card_data.get("power", "")
        toughness = card_data.get("toughness", "")

        # Create a dictionary in the new format
        formatted_card_data = {
            "name": card_name,
            "type": card_type,
            "manaCost": mana_cost,
            "rarity": rarity,
            "setCode": set_code,
            "text": text,
            "power": power,
            "toughness": toughness
        }

        # Add the formatted card data to the list
        new_format_cards.append(formatted_card_data)

    # Save the cards in the new format to the output JSON file
    with open(output_file, 'w') as file:
        json.dump(new_format_cards, file, indent=4)

# Specify the input and output file paths
input_file = "all_cards.json"
output_file = "all_cards_massaged.json"

# Convert and save the cards in the new format
convert_to_new_format(input_file, output_file)

print("Conversion completed. Cards saved in the new format as 'all_cards_massaged.json'.")
