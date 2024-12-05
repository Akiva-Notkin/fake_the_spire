import pandas as pd
import math
import toml

all_cards_df = pd.read_csv('Slay the Spire Reference - Cards.csv')

card_dicts = {}
current_card_dict = ''

for index, row in all_cards_df.iterrows():
    if isinstance(row['Type'], float) and math.isnan(row['Type']):
        current_card_dict = row['Name']
    else:
        if current_card_dict not in card_dicts:
            card_dicts[current_card_dict] = {}
        card_dicts[current_card_dict][row['Name']] = {'type': row['Type'], 'rarity': row['Rarity'], 'cost': row['Cost'],
                                                      'description': row['Description']}

already_made_cards = toml.load('../data/cards.toml')
ironclad_cards = card_dicts['Ironclad Cards']
for card_name, card_dict in ironclad_cards.items():
    if card_name.replace(' ', '_').lower() not in already_made_cards['cards']:
        print(card_name)