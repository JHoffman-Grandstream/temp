import json
from difflib import SequenceMatcher
import sys  # Added for sys.exit()

def load_json_file(filename):
    """Load data from a JSON file."""
    with open(filename, 'r') as file:
        return json.load(file)

def get_mana_value(mana_cost):
    """Calculate the total mana value from a mana cost string, accounting for both numeric and color symbols."""
    mana_value = 0
    numeric_value = ''
    for char in mana_cost:
        if char.isdigit():
            numeric_value += char  # Accumulate digit characters
        else:
            if numeric_value:
                mana_value += int(numeric_value)  # Convert accumulated digits to int and add to total
                numeric_value = ''  # Reset for next number
            if char.isalpha():
                mana_value += 1  # Count each color symbol as 1

    if numeric_value:
        mana_value += int(numeric_value)  # Handle any remaining number at the end

    return mana_value

def similar(a, b, fuzziness):
    """Measure the similarity of two strings with adjustable fuzziness."""
    return SequenceMatcher(None, a, b).ratio() >= fuzziness

def is_planeswalker(card_type):
    """Check if the card type includes 'Planeswalker'."""
    return 'Planeswalker' in card_type

def extract_unique_colors(mana_cost):
    """Extract unique colors from the mana cost, treating non-standard colors as colorless ('C'), and ignoring '{X}'."""
    standard_colors = {'B', 'W', 'U', 'R', 'G'}
    colors = set()
    for char in mana_cost:
        if char in standard_colors:
            colors.add(char)
        elif char.isalpha() and char != 'X':
            colors.add('C')  # Treat non-standard colors as colorless
    return colors

def find_highest_mana_card_of_color(lotr_cards, colors):
    """Find the card with the highest mana cost that matches the given colors."""
    best_card = None
    highest_mana_value = -1
    for card in lotr_cards:
        if all(color in card.get('manaCost', '') for color in colors):
            mana_value = get_mana_value(card['manaCost'])
            if mana_value > highest_mana_value:
                highest_mana_value = mana_value
                best_card = card
    return best_card

def find_strong_rare_creature_or_enchantment(lotr_cards, colors, card_type):
    """Find a strong creature or enchantment from the same colors, prioritizing mythic, then rare, then uncommon rarity."""
    best_card = None
    highest_power_toughness = -1
    rarities = ['mythic', 'rare', 'uncommon']  # Prioritize mythic, then rare, then uncommon

    for rarity in rarities:
        for card in lotr_cards:
            if card['type'].startswith(card_type) and card['rarity'] == rarity and all(color in card.get('manaCost', '') for color in colors):
                if 'Creature' in card_type:
                    power_toughness = sum(int(value) for value in [card.get('power', '0'), card.get('toughness', '0')] if value.isdigit())
                else:
                    power_toughness = 0  # Enchantments don't have power/toughness

                if power_toughness > highest_power_toughness:
                    highest_power_toughness = power_toughness
                    best_card = card

        if best_card:
            break  # Stop searching if a match is found in the current rarity

    return best_card

def rarity_match(mtg_rarity, lotr_rarity):
    """Compare rarities, treating any non-standard rarity as 'rare'."""
    if mtg_rarity not in ["common", "uncommon", "rare", "mythic"]:
        mtg_rarity = "rare"
    return mtg_rarity == lotr_rarity

def find_similar_cards(mtg_cards, lotr_cards, fuzziness):
    """Find similar cards between MTG and LOTR datasets with increasing fuzziness."""
    converted_cards = []
    for mtg_card in mtg_cards:
        best_match = None
        if is_planeswalker(mtg_card['type']):
            colors = extract_unique_colors(mtg_card.get('manaCost', ''))
            if 'C' in colors and len(colors) > 1:
                colors.discard('C') # Discard the colorless component if other colors are present
            best_match = find_strong_rare_creature_or_enchantment(lotr_cards, colors, "Creature")
            if not best_match and len(colors) > 1:
                # Try to find a match for each individual color
                for color in colors:
                    best_match = find_strong_rare_creature_or_enchantment(lotr_cards, {color}, "Creature")
                    if best_match:
                        break

            if not best_match:
                print(f"No match found for the planeswalker '{mtg_card['name']}' with any of the colors {colors}")
                sys.exit(1)  # Exit on error
        else:
            card_type = mtg_card['type']

            match_found = False  # Flag to check if a match is found
            while not best_match and fuzziness > 0:
                best_lotro_card_for_criteria = None  # The best matching LOTR card so far
                for lotr_card in lotr_cards:
                    # Check criteria with current fuzziness
                    type_match = similar(card_type, lotr_card['type'], fuzziness)
                    mtg_mana_value = get_mana_value(mtg_card.get('manaCost', ''))
                    lotr_mana_value = get_mana_value(lotr_card.get('manaCost', ''))
                    mana_match = mtg_mana_value == lotr_mana_value
                    power_toughness_match = similar(f"{mtg_card.get('power', '')}/{mtg_card.get('toughness', '')}",
                                                    f"{lotr_card.get('power', '')}/{lotr_card.get('toughness', '')}", fuzziness)

                    if type_match and rarity_match(mtg_card['rarity'], lotr_card['rarity']) and power_toughness_match:
                        if mana_match:
                            best_match = lotr_card
                            match_found = True  # A direct match was found
                            break
                        else:
                            # Check if this LOTR card is the best match so far for the given criteria
                            if best_lotro_card_for_criteria is None or lotr_mana_value > get_mana_value(best_lotro_card_for_criteria.get('manaCost', '')):
                                best_lotro_card_for_criteria = lotr_card

                if not best_match:
                    if best_lotro_card_for_criteria:
                        # Use the best matching LOTR card found so far for the given criteria
                        best_match = best_lotro_card_for_criteria
                        match_found = True
                    else:
                        # Decrease fuzziness to expand search
                        fuzziness -= 0.1

            if not best_match:
                # If no match found, explain why and print the criteria that might have failed
                criteria_values = {
                    'Card Type': card_type,
                    'Mana Cost': mtg_card.get('manaCost', ''),
                    'Rarity': mtg_card['rarity'],
                    'Power/Toughness': f"{mtg_card.get('power', '')}/{mtg_card.get('toughness', '')}"
                }
                failed_criteria = []  # List to store the failed criteria
                if not type_match:
                    failed_criteria.append("Card Type")
                if not mana_match:
                    # Check if it's a high-cost or very high-cost card and explain why
                    if mtg_mana_value > 10:
                        if mtg_mana_value > 15 and lotr_mana_value <= 15:
                            failed_criteria.append("Mana Cost (Very High Cost)")
                        else:
                            failed_criteria.append("Mana Cost (High Cost)")
                    else:
                        failed_criteria.append("Mana Cost")
                if not rarity_match(mtg_card['rarity'], lotr_card['rarity']):
                    failed_criteria.append("Rarity")
                if not power_toughness_match:
                    failed_criteria.append("Power/Toughness")

                print(f"No match found for '{mtg_card['name']}' with the following criteria: {criteria_values}")
                print(f"Failed criteria: {', '.join(failed_criteria)}")
                sys.exit(1)  # Exit on error

        if best_match:
            converted_cards.append({
                'mtg_card': mtg_card['name'],
                'lotr_card': best_match['name']
            })

    return converted_cards

# Paths to the JSON files
mtg_json_file = 'database.json'
lotr_json_file = 'lotr.json'

# Load the data from JSON files
mtg_cards = load_json_file(mtg_json_file)
lotr_cards = load_json_file(lotr_json_file)

# Initial fuzziness level (can be adjusted)
initial_fuzziness = 0.8

# Find similar cards and write them to 'converted.json'
converted_cards = find_similar_cards(mtg_cards, lotr_cards, initial_fuzziness)
if converted_cards:
    with open('converted.json', 'w') as outfile:
        json.dump(converted_cards, outfile, indent=4)
    print("Conversion completed. Check 'converted.json' for results.")
