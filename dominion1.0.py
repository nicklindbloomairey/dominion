# base cards - two players
# 60 copper, 40 silver, 30 gold
# 8 estate, 8 duchy, 8 province
# 10 curses

import random
import os

#-------------------------------------------------------------------------------
# DATA
#-------------------------------------------------------------------------------
supply_costs = {'copper':0, 'silver':3, 'gold':6, 'estate':2, 'duchy':5,
    'province':8, 'curse':0, 'cellar':2, 'moat':2, 'village':3,
    'merchant':3, 'workshop':3, 'smithy':4, 'remodel':4,
    'militia':4, 'market':5, 'mine':5}
card_type = {'copper':['treasure'], 'silver':['treasure'], 'gold':['treasure'],
    'estate':['victory'], 'duchy':['victory'],
    'province':['victory'], 'curse':['curse'], 'cellar':['action'],
    'moat':['action', 'reaction'], 'village':['action'],
    'merchant':['action'], 'workshop':['action'],
    'smithy':['action'], 'remodel':['action'],
    'militia':['action', 'attack'], 'market':['action'],
    'mine':['action']}
options = {'auto_play_treasures': True,
    'auto_skip_on_less_than_two_coins':True,
    'kingdom': ['cellar', 'moat', 'village',
    'merchant', 'workshop', 'smithy', 'remodel', 'militia', 'market',
    'mine'],
    'verbose': True,
    'showvp': False}

#-------------------------------------------------------------------------------
# GLOBALS
#-------------------------------------------------------------------------------
supply_num = {'copper':60, 'silver':40, 'gold':30, 'estate':8, 'duchy':8,
    'province':8, 'curse':10, 'cellar':10, 'moat':10, 'village':10,
    'merchant':10, 'workshop':10, 'smithy':10, 'remodel':10,
    'militia':10, 'market':10, 'mine':10}
trash = []
players = []

#-------------------------------------------------------------------------------
# ACTION CARD FUNCTIONS
#-------------------------------------------------------------------------------
def cellar(player):
    player['actions'] += 1
    discarded = 0
    while True:
        print_hand(player)
        # PLAYER INPUT
        if player['ai']:
            i = player['ai_package'].ai_cellar_discard(supply_num, player)
        else:
            i = input('discard which card [card] or [done]: ')
        if i == 'done':
            break
        if i not in player['hand']:
            console(i,'is not in your hand')
            continue
        player['hand'].remove(i)
        player['discard'].append(i)
        discarded += 1
    console('you draw',discarded,'cards')
    draw(player, discarded, verbose=True)

def moat(player):
    draw(player, 2, verbose=True)

def village(player):
    draw(player, 1, verbose=True)
    player['actions'] += 2

def merchant(player):
    draw(player, 1, verbose=True)
    player['actions'] += 1

def workshop(player):
    while True:
        if player['ai']:
            i = player['ai_package'].ai_workshop(supply_num, player)
        else:
            i = input('what card costing up to 4 would you like to gain? ')
        if i not in supply_costs:
            console('thats not a card in the supply')
            continue
        if supply_costs[i] > 4:
            console('thats too expensive')
            continue
        break
    gain(player, i)

def smithy(player):
    draw(player, 3, verbose=True)

def remodel(player):
    if len(player['hand']) < 1:
        console('you have nothing to remodel')
        return
    while True:
        print_hand(player)
        #PLAYER INPUT
        if player['ai']:
            i = player['ai_package'].ai_remodel_trash(supply_num, player)
        else:
            i = input('what card would you like to trash? ')
        if i not in player['hand']:
            console('thats not a card in your hand')
            continue
        break
    player['hand'].remove(i)
    trash.append(i)
    console('you trashed a',i)
    max_cost = supply_costs[i] + 2
    while True:
        text = 'what card would you like to gain, costing up to ' + str(max_cost) + ' coins: '
        #PLAYER INPUT
        if player['ai']:
            i = player['ai_package'].ai_remodel_gain(supply_num, player, max_cost)
        else:
            i = input(text)
        if i not in supply_costs:
            console('thats not a card in the supply')
            continue
        if supply_costs[i] > max_cost:
            console('thats too expensive')
            continue
        break
    gain(player, i)

def militia(player):
    global players
    console('ATTACK:',player['name'],'played a militia!')
    player['coins'] += 2

    #force other players to discard
    for other_player in players:
        if other_player is player:
            # player who played militia doesn't discard
            #console('MILITIA: skipping',other_player['name'])
            continue

        #check for more than 3 cards
        if len(other_player['hand']) <= 3:
            console(other_player['name'],' is already down to',len(other_player['hand']),plural('card',len(other_player['hand'])))
            continue
        #check for moat
        has_moat = False
        for card in other_player['hand']:
            if card == 'moat':
                has_moat == True
        if has_moat:
            console(other_player['name'],'had a moat!')
            continue
        #discard
        while len(other_player['hand']) > 3:
            if other_player['ai']:
                i = other_player['ai_package'].ai_militia_discard(supply_num, other_player)
            else:
                while True:
                    print_hand(other_player)
                    i = input('what would you like to discard: ')
                    if i not in other_player['hand']:
                        console('thats not a card in your hand')
                    else:
                        break
            console(other_player['name'],'discarded a',i)
            other_player['hand'].remove(i)
            other_player['discard'].append(i)

def market(player):
    draw(player, 1, verbose=True)
    player['actions'] += 1
    player['buys'] += 1
    player['coins'] += 1

def mine(player):
    #check the player has treasures they can mine
    mineable_cards = []
    choice = True
    for card in player['hand']:
        if card in ['copper', 'silver'] and card not in mineable_cards:
            mineable_cards.append(card)
    if len(mineable_cards) == 0:
        console('you have no cards to mine')
        return
    if len(mineable_cards) == 1:
        choice = False
        i = mineable_cards[0]
    while choice:
        #PLAYER INPUT
        if player['ai']:
            i = player['ai_package'].ai_mine(supply_num, player)
        else:
            i = input('what card would you like to mine? [copper] -> silver or [silver] -> gold: ')
        if i not in player['hand']:
            console('thats not a card in your hand')
        elif i == 'copper':
            break
        elif i == 'silver':
            break
        else:
            console('must be a copper or a silver')
    player['hand'].remove(i)
    trash.append(i)
    if i == 'copper':
        to_gain = 'silver'
    elif i == 'silver':
        to_gain = 'gold'
    player['hand'].append(to_gain)
    console('you gain a',to_gain,'to your hand')


action_functions = {'cellar':cellar, 'moat':moat, 'village':village,
                    'merchant':merchant, 'workshop':workshop, 'smithy':smithy,
                    'remodel':remodel, 'militia':militia, 'market':market,
                    'mine':mine}

#-------------------------------------------------------------------------------
# FUNCTIONS
#-------------------------------------------------------------------------------
def reset_supply():
    global supply_num
    supply_num = {'copper':60, 'silver':40, 'gold':30, 'estate':8, 'duchy':8,
                    'province':8, 'curse':10, 'cellar':10, 'moat':10, 'village':10,
                    'merchant':10, 'workshop':10, 'smithy':10, 'remodel':10,
                    'militia':10, 'market':10, 'mine':10}
def console(*text):
    if not options['verbose']:
        return
    print(*text)

def clear():
    if not options['verbose']:
        return
    os.system('clear')

def create_start_deck():
    return ['copper']*7 + ['estate']*3

def shuffle(list):
    for i in range(len(list)-1, -1, -1):
        j = random.randint(0,i)
        temp = list[i];
        list[i] = list[j]
        list[j] = temp

def gain(player, card):
    console('you gain a',card)
    player['discard'].append(card)
    supply_num[card] -= 1

def plural(str, count):
    if count == 1:
        return str
    else:
        return str + 's'

def draw(player, n, verbose=False):
    cards_drew = []
    for i in range(n):
        # shuffle discard to make new deck if no cards left
        if len(player['deck']) == 0:
            player['deck'] = player['discard']
            player['discard'] = []
            shuffle(player['deck'])
        #draw a card
        card = player['deck'].pop()
        player['hand'].append(card)
        cards_drew.append(card)
    if verbose:
        console('you drew',len(cards_drew),plural('card', len(cards_drew)) + ':',cards_drew)

def print_hand(player):
    console('hand:',player['hand'])

def print_play(player):
    console('play:',player['play'])

def print_cards(player):
    print_hand(player)
    console('discard:',player['discard'])
    console('deck:',player['deck'])

def count_coins(player):
    c = 0
    value = {'copper':1, 'silver':2, 'gold':3}
    c += sum(value[card] if card in value else 0 for card in player['play'])
    #Merchant
    merchant_n = player['play'].count('merchant')
    if 'silver' in player['play']:
        c += merchant_n
    return c

def get_card_type(card):
    if card not in card_type:
        return [] # no type
    return card_type[card]

def do_turn(player):
    player['coins'] = 0
    player['buys'] = 1
    player['actions'] = 1
    player['turns'] += 1
    #---------------------------------------------------------------------------
    #action phase
    #---------------------------------------------------------------------------
    console('---- action phase ----')
    #test if you have any action_cards
    have_actions = False
    for card in player['hand']:
        if 'action' in get_card_type(card):
            have_actions = True
    if not have_actions:
        player['actions'] = 0
    while player['actions'] > 0:
        print_hand(player)
        if player['actions'] > 1:
            console('you have',player['actions'],plural('action', player['actions']),'left')
        else:
            console('you have',player['actions'],'action left')
        if player['ai']:
            i = player['ai_package'].ai_action(supply_num, player)
        else:
            i = input('which ACTION card would you like to play? [card] or [done]: ')
        if i == 'done':
            break
        if i not in player['hand']:
            console(i,'is not in your hand')
        if 'action' not in get_card_type(i):
            console(i,'is not an action card')
            continue
        #play the card
        player['actions'] -= 1
        player['hand'].remove(i)
        player['play'].append(i)
        console('you play a',i)
        action_functions[i](player) # run the function corresponding to the card
        has_action_card_left = False
        for card in player['hand']:
            if 'action' in get_card_type(card):
                has_action_card_left = True
                break
        if not has_action_card_left:
            console('you have no more action cards left, moving to buy phase')
            break
        if player['actions'] == 0:
            console('you have no more actions left, moving to buy phase')

    #---------------------------------------------------------------------------
    # buy phase
    #---------------------------------------------------------------------------
    console('---- buy phase ----')
    # assuming player plays all their money
    if options['auto_play_treasures']:
        i = 0
        while i < len(player['hand']):
            if 'treasure' in get_card_type(player['hand'][i]):
                player['play'].append(player['hand'].pop(i))
            else:
                i += 1
    else:
        while True:
            #check the player has treasure cards
            has_treasure_card_left = False
            for card in player['hand']:
                if 'treasure' in get_card_type(card):
                    has_treasure_card_left = True
                    break
            if not has_treasure_card_left:
                console('you have no more treasure cards left')
                break
            i = input('what TREASURE would you like to play? [card] or [done]: ')
            if i == 'done':
                break
            if i not in player['hand']:
                console(i,'is not in your hand')
                continue
            if 'treasure' not in get_card_type(i):
                console(i,'is not an treasure card')
                continue
    player['coins'] += count_coins(player)
    print_hand(player)
    print_play(player)
    while player['buys'] > 0:
        console('you have',player['coins'],plural('coin', player['coins']),'and',
                player['buys'],plural('buy', player['buys']))
        # PLAYER INPUT
        if player['ai']:
            selection = player['ai_package'].ai_buy(supply_num, player)
        else:
            selection = input('what would you like to BUY? [card] or [done] ')
        if selection == 'done':
            console('you buy nothing')
            break # buy nothing
        if selection not in supply_costs:
            console('thats not a card, try again')
            continue
        if player['coins'] < supply_costs[selection]:
            console('that costs',supply_costs[selection])
            console('you cant afford that card, pick another')
            continue
        #card bought
        elif player['coins'] >= supply_costs[selection]:
            console('you bought a',selection,'for',str(supply_costs[selection]) + '!')
            gain(player, selection)
            player['coins'] -= supply_costs[selection]
            player['buys'] -= 1
        if player['buys'] == 0: # exit loop early
            break
        #handle extra buys
        console('you have',player['buys'],plural('buy', player['buys']),'left')
        if options['auto_skip_on_less_than_two_coins'] and player['coins'] < 2:
            console('skipping extra buys because you have less than two coins')
            break

    #---------------------------------------------------------------------------
    # clean up phase
    #---------------------------------------------------------------------------
    for i in range(len(player['hand'])):
        player['discard'].append(player['hand'].pop())
    for i in range(len(player['play'])):
        player['discard'].append(player['play'].pop())
    draw(player, 5)

def game_over():
    if supply_num['province'] < 1:
        return True
    count_empty = sum(1 if supply_num[card] < 1 else 0 for card in supply_num)
    if count_empty >= 3:
        return True
    return False

def count_vp(player):
    #move hand and discard to deck
    for i in range(len(player['hand'])):
        player['deck'].append(player['hand'].pop())
    for i in range(len(player['discard'])):
        player['deck'].append(player['discard'].pop())

    value = {'estate':1, 'duchy':3, 'province':6}
    return sum(value[card] if card in value else 0 for card in player['deck'])



#-------------------------------------------------------------------------------
# GAME START
#-------------------------------------------------------------------------------
def game(p1=None, p2=None, set_opt=None):
    global options
    global players
    if set_opt is not None:
        options.update(set_opt)

    reset_supply()
    turn = 1
    player1 = {'name': 'player1','ai':False,'ai_package':None,'id':1,
            'deck': create_start_deck(), 'hand': [],
            'discard': [], 'play':[], 'actions':1, 'coins':0, 'buys':1,
            'turns':0, 'vp':0}
    player2 = {'name': 'player2','ai':False,'ai_package':None,'id':1,
            'deck': create_start_deck(), 'hand': [],
            'discard': [], 'play':[], 'actions':1, 'coins':0, 'buys':1,
            'turns':0, 'vp':0}

    '''
    if type(p1) is not str:
        player1['name'] = p1.NAME
        player1['ai'] = True
        player1['ai_package'] = p1
    else:
        player1['name'] = p1
        player1['ai'] = False

    if type(p2) is not str:
        player2['name'] = p2.NAME
        player2['ai'] = True
        player2['ai_package'] = p2
    else:
        player2['name'] = p2
        player2['ai'] = False
    '''

    players = [player1, player2] # bundle
    for p in players:
        if p['ai']:
            p['ai_package'].KINGDOM = supply_costs
    shuffle(player1['deck'])
    shuffle(player2['deck'])
    draw(player1, 5)
    draw(player2, 5)

    # show welcome message
    clear()
    console('WELCOME TO DOMINION')
    console('')
    console('OPTIONS:')
    console('Auto Play Treasures:\t\t\t',options['auto_play_treasures'])
    console('Skip Extra Buys On Less Than 2 Coins:\t',options['auto_skip_on_less_than_two_coins'])
    console('Kingdom Cards:',options['kingdom'])
    console('')
    console('PLAYERS:')
    for i in range(len(players)):
        console('Player',str(i+1) + ':',players[i]['name'])
    console('')
    if options['verbose']:
        _blank = input('Press Return to start')

    # game loop
    while turn < 100:
        #console('\n\nturn',turn)
        clear()
        if turn == 1:
            turn_text = '1st'
        elif turn == 2:
            turn_text = '2nd'
        elif turn == 3:
            turn_text = '3rd'
        else:
            turn_text = str(turn) + 'th'
        console("player1's",turn_text,'turn. PROVINCES LEFT:',supply_num['province'])
        #print_cards(player1)
        do_turn(player1)
        #print_cards(player1)
        if game_over():
            break
        console('')
        console("player2's",turn_text,'turn. PROVINCES LEFT:',supply_num['province'])
        #print_cards(player2)
        do_turn(player2)
        if options['verbose']:
            _blank = input('hit return to continue')
        print_cards(player2)
        if game_over():
            break
        turn += 1

    #GAME IS OVER
    clear()
    console('The game has ended!\n')

    for p in players:
        p['vp'] = count_vp(p)
        console(p['name'],'has',p['vp'],'victory points','and had',p['turns'],'turns')

    # find winner
    winner = players[0]
    tie = None
    for p in players:
        if p is winner:
            continue
        if p['vp'] > winner['vp']:
            winner = p
            tie = None
        elif p['vp'] == winner['vp']:
            #tie breaker
            if p['turns'] < winner['turns']:
                winner = p
            elif p['turns'] == winner['turns']:
                tie = p

    #print who won
    if tie is None:
        console(winner['name'],'won the game!')
    else:
        console(winner['name'],'and',tie['name'],'tied!')

    if tie is not None:
        return len(players)
    return players.index(winner)

if __name__ == '__main__':
    game()
