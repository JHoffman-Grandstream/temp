
import json
from difflib import SequenceMatcher

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

def find_strong_rare_creature(lotr_cards, colors):
    """Find a strong creature from the same colors, prioritizing mythic, then rare, then uncommon rarity."""
    best_card = None
    highest_power_toughness = -1
    rarities = ['mythic', 'rare', 'uncommon']  # Prioritize mythic, then rare, then uncommon

    for rarity in rarities:
        for card in lotr_cards:
            if card['type'].startswith('Creature') and card['rarity'] == rarity and all(color in card.get('manaCost', '') for color in colors):
                power_toughness = sum(int(value) for value in [card.get('power', '0'), card.get('toughness', '0')] if value.isdigit())
                if power_toughness > highest_power_toughness:
                    highest_power_toughness = power_toughness
                    best_card = card

        if best_card:
            break  # Stop searching if a match is found in the current rarity

    # Print the unique colors considered for the match
    # print("Searching for a strong creature with unique colors:", colors, "and rarity:", rarity)

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
            best_match = find_strong_rare_creature(lotr_cards, colors)
            if not best_match and len(colors) > 1:
                # Try to find a match for each individual color
                for color in colors:
                    best_match = find_strong_rare_creature(lotr_cards, {color})
                    if best_match:
                        break

            if not best_match:
                print(f"No match found for the planeswalker '{mtg_card['name']}' with any of the colors {colors}")
        else:
            while not best_match and fuzziness > 0:
                for lotr_card in lotr_cards:
                    # Check criteria with current fuzziness
                    type_match = similar(mtg_card['type'], lotr_card['type'], fuzziness)
                    mana_match = get_mana_value(mtg_card.get('manaCost', '')) == get_mana_value(lotr_card.get('manaCost', ''))
                    power_toughness_match = similar(f"{mtg_card.get('power', '')}/{mtg_card.get('toughness', '')}",
                                                    f"{lotr_card.get('power', '')}/{lotr_card.get('toughness', '')}", fuzziness)

                    if type_match and mana_match and rarity_match(mtg_card['rarity'], lotr_card['rarity']) and power_toughness_match:
                        best_match = lotr_card
                        break

                if not best_match:
                    # Decrease fuzziness to expand search
                    fuzziness -= 0.1

            # If no exact type match found, try matching with any creature
            if not best_match:
                for lotr_card in lotr_cards:
                    if 'Creature' in lotr_card['type'] and rarity_match(mtg_card['rarity'], lotr_card['rarity']):
                        best_match = lotr_card
                        break

            # mtg_mana_value = get_mana_value(mtg_card.get('manaCost', ''))
            # print(f"Mana value for '{mtg_card['name']}': {mtg_mana_value}")
            # If still no match found, check for high mana cost
            if not best_match and get_mana_value(mtg_card.get('manaCost', '')) > 6: # Assuming 6 as the threshold for high mana cost
                colors = extract_unique_colors(mtg_card.get('manaCost', ''))
                best_match = find_highest_mana_card_of_color(lotr_cards, colors)
                if not best_match:
                    print(f"No high mana cost match found for '{mtg_card['name']}' with colors {colors}")

        if best_match:
            converted_cards.append({
                'mtg_card': mtg_card['name'],
                'lotr_card': best_match['name'],
                'setCode': mtg_card['setCode']
            })
        else:
            print(f"No match found for '{mtg_card['name']}' with the current fuzziness level {fuzziness}")
            break

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
