import json
import os
import re
import shutil
import sys

def load_converted_cards(filename='converted.json'):
    """Load the converted cards mapping from a JSON file."""
    with open(filename, 'r') as file:
        converted_cards = json.load(file)
    
    # Ignore 'setCode' and only store the card name mapping
    return {card['mtg_card']: card['lotr_card'] for card in converted_cards}

def extract_card_name(card_info):
    """Extract the card name from the card information."""
    card_name_parts = card_info.split('|', 1)  # Split only once
    if card_name_parts:
        card_name = card_name_parts[1].strip()  # Use the second part
        return card_name
    return None

def convert_deck_file(input_path, output_dir, conversion_map, converted_cards):
    """Convert a single deck file using the provided conversion map and save it to a new directory."""
    with open(input_path, 'r') as file:
        lines = file.readlines()

    converted_lines = []
    found_main = False  # Flag to track when [Main] section starts
    found_sideboard = False  # Flag to track when [Sideboard] section starts
    metadata_lines = []  # Store metadata lines

    for line_number, line in enumerate(lines, start=1):  # Track line numbers
        line = line.strip()
        if line.startswith("[Main]"):
            found_main = True
            metadata_lines.append(line)  # Include [Main] in metadata
            continue  # Skip the "[Main]" section header
        elif line.startswith("[Sideboard]"):
            found_sideboard = True
            metadata_lines.append(line)  # Include [Sideboard] in metadata
            continue  # Skip the "[Sideboard]" section header
        elif line.startswith("[") and "]" in line:
            # Preserve lines with brackets intact
            metadata_lines.append(line)
        elif found_main or found_sideboard:
            if line:  # Check if the line is not empty
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    card_count, card_info = parts
                    card_name_parts = card_info.split('|')
                    if len(card_name_parts) >= 1:
                        card_name = card_name_parts[0].strip()
                        # Check if the card name is in the list of exceptions
                        if card_name in ("Forest", "Swamp", "Plains", "Mountain", "Island"):
                            # Replace with the same quantity and type but change the set to |LTR
                            converted_line = f"{card_count} {card_name}|LTR"
                            converted_lines.append(converted_line)
                        elif card_name in conversion_map:
                            lotr_card = conversion_map[card_name]  # Ignore set information
                            set_code = next(card['setCode'] for card in converted_cards if card['mtg_card'] == card_name)
                            converted_line = f"{card_count} {lotr_card}|{set_code}"
                            converted_lines.append(converted_line)
                        else:
                            print(f"Card not found in file '{input_path}' on line {line_number}: {line}")  # Print notice
                            converted_lines.append(line)  # Keep the original card in place
                    else:
                        converted_lines.append(line)
                        print(f"Invalid line in file '{input_path}' on line {line_number}: {line}")  # Print filename and line
                        sys.exit(1)  # Exit on the first error
                else:
                    converted_lines.append(line)
                    print(f"Invalid line in file '{input_path}' on line {line_number}: {line}")  # Print filename and line
                    sys.exit(1)  # Exit on the first error
        else:
            metadata_lines.append(line)  # Store metadata lines before [Main]

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save the converted deck to the output directory with the same filename
    output_filename = os.path.basename(input_path)
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w') as file:
        file.write('\n'.join(metadata_lines + ['[Main]'] + converted_lines))

def convert_all_deck_files(input_dir, output_dir, conversion_map, converted_cards):
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

                # Convert the deck file and save it to the output directory
                convert_deck_file(input_path, output_subdir, conversion_map, converted_cards)

# Load the conversion map from converted.json
conversion_map = load_converted_cards()

# Load the converted cards list from converted.json
converted_cards = json.load(open('converted.json', 'r'))

# Paths to the input and output directories
input_dir = 'decks'  # Replace with the path to your input directory
output_dir = 'decks2'  # Replace with the path to your output directory

# Convert all .dck files in the input directory and save them to the output directory
convert_all_deck_files(input_dir, output_dir, conversion_map, converted_cards)

print("Conversion of deck files complete.")
