'''
helper.py

stand alone helper functions for dominion
this file exists solely to make the other one smaller
'''
import random
import json

#-------------------------------------------------------------------------------
# Load json files
#-------------------------------------------------------------------------------
with open('card_type.json') as f:
    card_type = json.load(f)
with open('card_costs.json') as f:
    card_costs = json.load(f)
with open('card_text.json') as f:
    card_text = json.load(f)

#-------------------------------------------------------------------------------
# helper functions
#-------------------------------------------------------------------------------
def in_supply(card):
    ''' returns true if card is in supply, false otherwise
    currently, just check if card has a cost
    '''
    return True if costs(card) >= 0 else False

def get_card_text(card):
    ''' returns the list of lines of card text
    '''
    return card_text[card]

def create_start_deck():
    ''' returns list of 7 coppers and 3 estates '''
    return ['copper']*7 + ['estate']*3

def shuffle(list):
    ''' fisher-yates shuffle '''
    for i in range(len(list)-1, -1, -1):
        j = random.randint(0,i)
        temp = list[i];
        list[i] = list[j]
        list[j] = temp
    return

def plural(string, count):
    ''' adds an 's' if count is not one '''
    if count == 1:
        return string
    return string + 's'

def a(nextword):
    ''' returns 'an' if next word starts with a vowel sound, otherwise 'a' '''
    vowel_starting_sound = ['estate']
    if nextword in vowel_starting_sound:
        return 'an '+nextword
    return 'a '+nextword

def count_coins(player):
    ''' count how many coins the player has, return number of coins
    watches for merchant
    '''
    c = 0
    value = {'copper':1, 'silver':2, 'gold':3}
    c += sum(value[card] if card in value else 0 for card in player['play'])
    #Merchant
    merchant_n = player['play'].count('merchant')
    if 'silver' in player['play']:
        c += merchant_n
    return c

def get_card_type(card):
    ''' returns a list of the card types '''
    if card not in card_type:
        return [] # no type, most likely not a card as all cards have types
    return card_type[card]

def has_card_type(hand, type):
    ''' does this hand have any cards of the specified type in it? 
    return true or false 
    '''
    for card in hand:
        if type in get_card_type(card):
            return True
    return False

def has_action_card(hand):
    return has_card_type(hand, 'action')

def has_treasure_card(hand):
    return has_card_type(hand, 'treasure')

def count_vp(p):
    ''' count up victory points for player p'''
    cards = p['deck']+p['hand']+p['play']+p['discard']
    value = {'estate':1, 'duchy':3, 'province':6, 'curse':-1}
    return sum(value[card] if card in value else 0 for card in cards)

def costs(card):
    ''' returns how much card costs, return -1 if no cost '''
    if card in card_costs:
        return card_costs[card]
    return -1
