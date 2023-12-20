import json
import os
import re
import shutil
import sys  # Import sys module for exiting on error

def load_converted_cards(filename='converted.json'):
    """Load the converted cards mapping from a JSON file."""
    with open(filename, 'r') as file:
        converted_cards = json.load(file)
    return {card['mtg_card']: (card['lotr_card'], card['setCode']) for card in converted_cards}

def convert_deck_file(input_path, output_dir, conversion_map):
    """Convert a single deck file using the provided conversion map and save it to a new directory."""
    with open(input_path, 'r') as file:
        lines = file.readlines()

    converted_lines = []
    for line_number, line in enumerate(lines, start=1):  # Track line numbers
        if line.startswith(('2 ', '4 ', '1 ')):
            card_info = re.split(r' \|', line.strip())
            if len(card_info) >= 2:  # Check if card_info has at least 2 elements
                card_name = card_info[1]
                if card_name in conversion_map:
                    lotr_card, set_code = conversion_map[card_name]
                    converted_line = f"{card_info[0]} {lotr_card}|{set_code}|1\n"
                    converted_lines.append(converted_line)
                else:
                    converted_lines.append(line)
                    print(f"Card not found on line {line_number}: {line.strip()}")  # Print line number
                    sys.exit(1)  # Exit on the first error
            else:
                converted_lines.append(line)
                print(f"Card not found on line {line_number}: {line.strip()}")  # Print line number
                sys.exit(1)  # Exit on the first error
        else:
            converted_lines.append(line)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save the converted deck to the output directory with the same filename
    output_path = os.path.join(output_dir, os.path.basename(input_path))
    with open(output_path, 'w') as file:
        file.writelines(converted_lines)

def convert_all_deck_files(input_dir, output_dir, conversion_map):
    """Convert all .dck files in the input directory and save them to the output directory."""
    # Delete the output directory if it exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith('.dck'):
                input_path = os.path.join(root, filename)
                relative_path = os.path.relpath(input_path, input_dir)
                output_subdir = os.path.join(output_dir, os.path.dirname(relative_path))
                convert_deck_file(input_path, output_subdir, conversion_map)

# Load the conversion map from converted.json
conversion_map = load_converted_cards()

# Paths to the input and output directories
input_dir = 'decks'  # Replace with the path to your input directory
output_dir = 'decks2'  # Replace with the path to your output directory

# Convert all .dck files in the input directory and save them to the output directory
convert_all_deck_files(input_dir, output_dir, conversion_map)

print("Conversion of deck files complete.")
