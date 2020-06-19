# base cards - two players
# 60 copper, 40 silver, 30 gold
# 8 estate, 8 duchy, 8 province
# 10 curses

# 128 x 30
# stand alone helper functions
from helper import *

import curses
import curses.textpad
import smithy_big_money
import big_money

#-------------------------------------------------------------------------------
# OPTIONS
#-------------------------------------------------------------------------------
kingdom = ['cellar', 'moat', 'village', 'merchant', 'workshop',
    'smithy', 'remodel', 'militia', 'market', 'mine']
options = {
    'auto_play_treasures': True,
    'auto_skip_on_less_than_two_coins':True,
    'kingdom': kingdom,
    'verbose': True,
    'showvp': False,
    'showdeck': False,
    'assumemineprogression': True,
    'players': [('SBM',smithy_big_money), ('nic', None), ('sam', None),
    ('big',big_money)],
}

#-------------------------------------------------------------------------------
# GLOBALS
#-------------------------------------------------------------------------------
supply_num = {'copper':60, 'silver':40, 'gold':30, 'estate':8, 'duchy':8,
    'province':8, 'curse':10}
for card in kingdom:
    supply_num[card] = 10
trash_pile = []
players = []
line = 1 # the line number of the console info to be printed onto next
turn = 0

#windows
sc = None #console area
supply = None # supply amounts
handwin = None # hand window
playwin = None # play window
helpwin = None # help text window
statswin = [] # deck list windows

#-------------------------------------------------------------------------------
# ACTION CARD FUNCTIONS
#-------------------------------------------------------------------------------
def cellar(player):
    ''' Cellar [action]
    +1 action
    discard any number of cards, draw one card per card discarded
    '''
    player['actions'] += 1
    discarded = 0
    while True:
        print_hand(player)
        # PLAYER INPUT
        if player['ai'] is not None:
            i = player['ai'].ai_cellar_discard(supply_num, player)
        else:
            i = get_input('discard which card [card] or [done]: ')
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
    return

def moat(player):
    ''' Moat [action, reaction]
    +2 cards
    reveal from hand to do make you immune to attack
    '''
    draw(player, 2, verbose=True)
    return

def village(player):
    ''' Village [action]
    +1 card
    +2 actions
    '''
    draw(player, 1, verbose=True)
    player['actions'] += 2
    return

def merchant(player):
    ''' merchant [action]
    +1 card
    +1 action
    first time you play a silver, +1 coin
    '''
    draw(player, 1, verbose=True)
    player['actions'] += 1
    return

def workshop(player):
    ''' workshop [action]
    gain a card costing up to 4
    '''
    while True:
        if player['ai'] is not None:
            card = player['ai'].ai_workshop(supply_num, player)
        else:
            card = get_input('what card costing up to 4 would you like to gain? ')
        if not in_supply(card):
            console('thats not a card in the supply')
            continue
        if costs(card) > 4:
            console('thats too expensive')
            continue
        break
    gain(player, card)
    return

def smithy(player):
    ''' smithy [action]
    +3 cards
    '''
    draw(player, 3, verbose=True)
    return

def remodel(player):
    ''' remodel [action]
    trash a card from hand
    gain a card costing up to 2 more than trashed card
    '''
    if len(player['hand']) < 1:
        console('you have nothing to remodel')
        return
    while True:
        print_hand(player)
        #PLAYER INPUT
        if player['ai'] is not None:
            card = player['ai'].ai_remodel_trash(supply_num, player)
        else:
            card = get_input('what card would you like to trash? ')
        if card not in player['hand']:
            console('thats not a card in your hand')
            continue
        break
    trash(player, card)
    max_cost = costs(card) + 2
    while True:
        #PLAYER INPUT
        if player['ai'] is not None:
            card = player['ai'].ai_remodel_gain(supply_num, player, max_cost)
        else:
            text = 'what card would you like to gain, costing up to '+str(max_cost)+' coins: '
            card = get_input(text)
        if not in_supply(card):
            console('thats not a card in the supply')
            continue
        if costs(card) > max_cost:
            console('thats too expensive')
            continue
        break
    gain(player, card)
    return

def militia(player):
    ''' Militia [action, attack]
    +2 coins
    other players discard down to 3 cards
    '''
    global players
    console('ATTACK:',player['name'],'played a militia!')
    player['coins'] += 2

    #force other players to discard
    for other_player in players:
        if other_player is player:
            # player who played militia doesn't discard
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
                break
        if has_moat:
            console(other_player['name'],'had a moat!')
            continue
        #discard
        discarded_cards = []
        while len(other_player['hand']) > 3:
            print_hand(other_player)
            while True: # select card loop
                if other_player['ai'] is not None:
                    card = other_player['ai'].ai_militia_discard(supply_num, other_player)
                else:
                    card = get_input('what would you like to discard: ')
                if card not in other_player['hand']:
                    console('thats not a card in your hand')
                    continue
                break # card selected
            discarded_cards.append(card)
            other_player['hand'].remove(card)
            other_player['discard'].append(card)
        console(other_player['name'],'discarded: ',''.join([x+' ' for x in discarded_cards]))
    return

def market(player):
    ''' Market [action]
    +1 card
    +1 action
    +1 buy
    +1 coin
    '''
    draw(player, 1, verbose=True)
    player['actions'] += 1
    player['buys'] += 1
    player['coins'] += 1
    return

def mine(player):
    ''' Mine [action]
    trash a treasure
    gain a treasure costing up to 3 more than trashed card
    '''
    if len(player['hand']) < 1 or not has_treasure_card(player['hand']):
        console('you have nothing to mine')
        return
    # option - assumemineprogression
    treasures = []
    progression = {'copper':'silver', 'silver':'gold'}
    if options['assumemineprogression']: # check if we only have one type of treasure
        for card in player['hand']:
            if 'treasure' in get_card_type(card) and card not in treasures:
                treasures.append(card)
        if len(treasures) == 1 and treasures[0] in progression:
            trash(player, treasures[0])
            gain(player, progression[treasures[0]], dest='hand')
            return
    # card to trash
    while True:
        print_hand(player)
        #PLAYER INPUT
        if player['ai'] is not None:
            card = player['ai'].ai_mine_trash(supply_num, player)
        else:
            card = get_input('what treasure card would you like to trash? ')
        if card == 'done':
            return # dont mine anything
        if card not in player['hand']:
            console('thats not a card in your hand')
            continue
        if 'treasure' not in get_card_type(card):
            console('thats not a treasure card')
            continue
        break
    trash(player, card)
    max_cost = costs(card) + 3
    #option - assumemineprogression
    if options['assumemineprogression']:
        gain(player, progression[card], dest='hand')
        return
    while True:
        #PLAYER INPUT
        if player['ai'] is not None:
            card = player['ai'].ai_mine_gain(supply_num, player, max_cost)
        else:
            text = 'what treasure card would you like to gain, costing up to '+str(max_cost)+' coins: '
            card = get_input(text)
        if not in_supply(card):
            console('thats not a card in the supply')
            continue
        if costs(card) > max_cost:
            console('thats too expensive')
            continue
        break
    gain(player, card, dest='hand')
    return

# dictionary to call functions
action_functions = {'cellar':cellar, 'moat':moat, 'village':village,
                    'merchant':merchant, 'workshop':workshop, 'smithy':smithy,
                    'remodel':remodel, 'militia':militia, 'market':market,
                    'mine':mine}

#-------------------------------------------------------------------------------
# FUNCTIONS
#-------------------------------------------------------------------------------
def reset_supply(n=2):
    ''' resets the supply amounts
    n - number of players
    '''
    global supply_num
    estate_and_duchy = {2:8, 3:12, 4:12, 5:12, 6:12}
    curse = (n-1)*10
    province = {2:8, 3:12, 4:12, 5:15, 6:18}
    supply_num = {'copper':60,'silver':40,'gold':30,'estate':estate_and_duchy[n],
        'duchy':estate_and_duchy[n],'province':province[n],'curse':curse}
    for card in kingdom:
        supply_num[card] = 10
    return

def console(*text):
    ''' same as print(text) but for the curses implementation
    it adds a line of text to the console info area, scrolling if needed
    '''
    global line
    if not options['verbose']:
        return
    #print(*text)
    if line >= 16:
        sc.addstr(16, 1,''.join([str(x)+' ' for x in text])) 
        sc.scroll()
    else:
        sc.addstr(line, 1,''.join([str(x)+' ' for x in text])) 
    sc.clrtoeol()
    sc.box()
    line += 1
    return

def clear():
    ''' clears the console info area
    '''
    global line
    line = 1
    if not options['verbose']:
        return
    #os.system('clear')
    sc.erase()
    sc.box()
    sc.addstr(22,1,'type "help [card]" for that cards text')
    sc.refresh()
    return

def update_stats():
    ''' updates and redraws the deck list windows
    '''
    if not options['showdeck']:
        return
    for i in range(2):
        # update deck stats
        statswin[i].erase()
        count = {}
        p = players[i]
        cards = p['deck']+p['hand']+p['play']+p['discard']
        statswin[i].addstr(1,18,'total '+str(len(cards)))
        statswin[i].addstr(2,18,'vp '+str(count_vp(p)))
        for card in cards:
            count[card] = cards.count(card)
        sorted_count = sorted(count.items(), key=lambda e:e[1], reverse=True)
        k = 0
        for j in range(8):
            if k >= len(sorted_count):
                break
            card = sorted_count[j][0]
            num = sorted_count[j][1]
            statswin[i].addstr(j+1,1,card+' ')
            statswin[i].addstr(j+1,10,str(num))
            k+=1
        for j in range(5):
            if k >= len(sorted_count):
                break
            card = sorted_count[j+8][0]
            num = sorted_count[j+8][1]
            statswin[i].addstr(j+4,1+17,card+' ')
            statswin[i].addstr(j+4,10+17,str(num))
            k+=1
        statswin[i].box()
        statswin[i].addstr(0, 2, p['name']+"'s"+' deck')
        statswin[i].refresh()
    return

def trash(player, card):
    ''' "trash" events go here?
    '''
    player['hand'].remove(card)
    trash_pile.append(card)
    console('you trashed',a(card))
    return

def buy(player, card):
    ''' "buy" events go here?
    '''
    console('you bought a',card,'for',str(costs(card)) + '!')
    gain(player, card)
    player['coins'] -= costs(card)
    player['buys'] -= 1
    return

def gain(player, card, dest='discard'):
    ''' "gain" effects should go here?
    adds a card to players discard
    subtract from supply
    if dest is set, put card there instead
    '''
    if supply_num[card] < 1:
        console('there are no',card,'left')
        return
    if dest is not 'discard':
        console('you gain',a(card),'to your',dest)
    else:
        console('you gain',a(card))
    supply_num[card] -= 1
    player[dest].append(card)
    update_supply()
    update_stats()
    return

def draw(player, n, verbose=False):
    ''' draw n cards, shuffle discard as new deck if necessary '''
    cards_drew = []
    for i in range(n):
        # shuffle discard to make new deck if no cards left
        if len(player['deck']) == 0:
            player['deck'] = player['discard']
            player['discard'] = []
            shuffle(player['deck'])
        # if you still have no cards, then you are done drawing.
        if len(player['deck']) == 0:
            break
        #draw a card
        card = player['deck'].pop()
        player['hand'].append(card)
        cards_drew.append(card)
    if verbose:
        console('you drew',len(cards_drew),plural('card', len(cards_drew)) + ':',cards_drew)

def print_hand(player):
    ''' update hand window '''
    #console('hand:',player['hand'])
    #handwin.addstr(1,1,str(player['hand']))
    hand = ''.join([x+' ' for x in player['hand']])
    handwin.addnstr(1,1,hand,60)
    handwin.clrtobot() # clear excess characters
    handwin.box()
    handwin.addstr(0,2,'hand')
    handwin.refresh()

def print_play(player):
    ''' update play window '''
    #playwin.addstr(1,1,str(player['play']))
    play = ''.join([x+' ' for x in player['play']])
    playwin.addnstr(1,1,play,60)
    playwin.clrtobot()
    playwin.box()
    playwin.addstr(0,2,'play')
    playwin.refresh()


def get_input(prompt):
    ''' curses friendly replacement for input()
    create a textbox, let user type something out, and return what they type
    delete the textbox after
    '''
    written = ''
    def validator(char):
        ''' ONLY CALLED IN get_input
        this function is passed to the edit() function of the textbox
        it is called on every key press to watch for bad keypresses?
        return new keypress we want to use

        we make a few calls to tb.do_command()
        '''
        nonlocal written
        if char == ord('#'):
            exit()
        if char == 127: # 127 = backspace
            return 263 # control-h which acts as backspace
        # tab complete
        elif char == 9: # 9 = tab
            if written is '':
                written = tb.gather()
            for card in list(card_costs):
                if card == tb.gather().strip():
                    continue
                if card.startswith(written.strip()):
                    #delete current stuff
                    for i in range(len(tb.gather())):
                        tb.do_command(263)
                    # fake type in the card name
                    for i in range(len(card)):
                        tb.do_command(ord(card[i]))
                    break
            return char
        written = '' # if we didn't press tab reset the var for tab complete.
        return char
    # BEGIN get_input()
    #global tb # so that validator() can use it
    h, w, y, x = (1, 20, 25, 2)
    sc.addstr(y-2-6, x-1, prompt)
    sc.clrtoeol()
    sc.box()
    #make a text box
    win = curses.newwin(h, w, y, x)
    # draw a nice rectangle around text box
    curses.textpad.rectangle(sc, y-1-6, x-1, y+h-6, x+w)
    sc.refresh()
    tb = curses.textpad.Textbox(win)
    text = tb.edit(validator).strip() #wait for user to input text
    # delete the text box
    del win
    del tb

    # help text control
    if text[:4] == 'help':
        card = text[4:].strip()
        i = 2
        helpwin.erase()
        helpwin.box()
        helpwin.addstr(0, 2, 'help')
        helpwin.addstr(1, 2, card, curses.A_UNDERLINE)
        if card not in card_text:
            # not an actual card, retry getting input
            return get_input(prompt)
        for line in card_text[card]:
            helpwin.addstr(i, 2, line)
            i+=1
        helpwin.refresh()
        return get_input(prompt)

    #clear that nice rectangle
    for i in range(18, 21):
        sc.move(i, 0)
        sc.clrtoeol()
    sc.box()
    
    sc.refresh()
    return text

def wait_for_player():
    ''' waits for player to press a key until continuing '''
    sc.addstr(25-2-6, 2-1, 'press any key to continue')
    sc.clrtoeol()
    sc.box()
    sc.refresh()
    # needs to be in delay mode
    sc.getkey() # this pauses the program, we dont do anything with the keypress
    return

def update_supply():
    ''' updates and redraws the supply number window 
    NOW IN COLOR
    colors:
    1 - white 
    2 - green
    3 - yellow
    4 - magenta
    '''
    supply.erase()
    supply.box()

    i = 0
    spacer = 14
    supply.addstr(0, 2, 'The Supply', curses.A_UNDERLINE)
    supply.addstr(1, 4, 'card', curses.A_UNDERLINE)
    supply.addstr(1, spacer-2, 'cost', curses.A_UNDERLINE)
    supply.addstr(1, spacer + 4, 'num', curses.A_UNDERLINE)
    for card in list(card_costs):
        color = curses.color_pair(1)
        if 'victory' in get_card_type(card):
            color = curses.color_pair(2)
        elif 'treasure' in get_card_type(card):
            color = curses.color_pair(3)
        elif 'curse' in get_card_type(card):
            color = curses.color_pair(4)
        supply.addstr(2+i, 2, card, color)
        supply.addstr(2+i, spacer, str(costs(card)), color)
        supply.addstr(2+i, spacer+4, str(supply_num[card]), color)
        i += 1
    supply.refresh()

def game_over():
    ''' check if the game is over, return true or false '''
    if supply_num['province'] < 1: # no provinces left
        return True
    count_empty = sum(1 if supply_num[card] < 1 else 0 for card in supply_num)
    if count_empty >= 3:
        return True
    return False

def create_player(name='player',ai=None):
    if ai is not None and name is not 'player':
        name = ai.NAME
    n = len(players) + 1
    player = {'name':name,'ai':ai,'id':n,'deck':create_start_deck(),'hand':[],
        'discard':[],'play':[],'actions':1,'coins':0,'buys':1,'turns':0,'vp':0}
    return player

def do_turn(player):
    ''' single turn for player
    first set the players coins, buys, actions.
    action phase - play actions
    buy phase - buy cards
    clean up - all cards move to discard
    '''
    player['coins'] = 0
    player['buys'] = 1
    player['actions'] = 1
    player['turns'] += 1

    #---------------------------------------------------------------------------
    # action phase
    #---------------------------------------------------------------------------
    # check we actually have action cards
    while player['actions'] > 0 and has_action_card(player['hand']): # main action phase loop
        # update views
        print_hand(player)
        print_play(player)
        # 'you have # action(s) left'
        console('you have',player['actions'],plural('action', player['actions']),'left')
        if player['ai'] is not None:
            card = player['ai'].ai_action(supply_num, player)
        else:
            card = get_input('which ACTION card would you like to play? [card] or [done]: ')
        if card == 'done':
            break
        if card not in player['hand']:
            console(card,'is not in your hand')
            continue
        if 'action' not in get_card_type(card):
            console(card,'is not an action card')
            continue
        #play the card
        player['actions'] -= 1
        player['hand'].remove(card)
        player['play'].append(card)
        console('you play',a(card)) # you play a(n) [card]
        action_functions[card](player) # run the function corresponding to the card

    #---------------------------------------------------------------------------
    # buy phase
    #---------------------------------------------------------------------------
    if options['auto_play_treasures']:
        i = 0
        while i < len(player['hand']):
            if 'treasure' in get_card_type(player['hand'][i]):
                player['play'].append(player['hand'].pop(i))
            else:
                i += 1
    else:
        while has_treasure_card(player['hand']): # treasure playing loop
            if player['ai'] is not None:
                card = player['ai'].ai_treasure(supply_num, player)
            else:
                card = get_input('what TREASURE would you like to play? [card] or [done]: ')
            if card == 'done':
                break
            if card not in player['hand']:
                console(card,'is not in your hand')
                continue
            if 'treasure' not in get_card_type(card):
                console(card,'is not an treasure card')
                continue
            # play treasure
            player['hand'].remove(card)
            player['play'].append(card)
    #increment coins so we dont overwrite coins from militia for example
    player['coins'] += count_coins(player)
    print_hand(player)
    print_play(player)
    while player['buys'] > 0: # buy loop
        # 'you have # coin(s) and # buy(s) left'
        console('you have',player['coins'],plural('coin', player['coins']),'and',
                player['buys'],plural('buy', player['buys']))
        # PLAYER INPUT
        if player['ai'] is not None:
            card = player['ai'].ai_buy(supply_num, player)
        else:
            card = get_input('what would you like to BUY? [card] or [done] ')
        if card == 'done':
            console('you buy nothing')
            break # buy nothing 
        if not in_supply(card):
            console('thats not a card in the supply, try again')
            continue
        if player['coins'] < costs(card):
            # 'that costs # and you only have #'
            console('that costs',costs(card),'and you only have',
                player['coins'])
            continue
        #card bought
        buy(player, card)
        #handle extra buys
        if options['auto_skip_on_less_than_two_coins'] and player['coins'] < 2 \
            and player['buys'] > 0:
            console('skipping extra buys because you have less than two coins')
            break

    #---------------------------------------------------------------------------
    # clean up phase
    #---------------------------------------------------------------------------
    for i in range(len(player['hand'])):
        player['discard'].append(player['hand'].pop())
    for i in range(len(player['play'])):
        player['discard'].append(player['play'].pop())
    draw(player, 5) #draw new hand

#-------------------------------------------------------------------------------
# GAME START
#-------------------------------------------------------------------------------
def game(scr, p1=None, p2=None, set_opt=None):
    global options
    global players
    global sc
    global supply
    global handwin
    global playwin
    global helpwin
    global statsp1
    global statsp2
    global turn
    for n, ai in options['players']:
        players.append(create_player(n, ai)) 
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    sc = scr
    y, x = sc.getmaxyx()
    sc.resize(y-6, round(x/2))
    sc.mvwin(6,0)
    supply = curses.newwin(len(card_costs)+3, 30, 0,round(x/2))
    sc.setscrreg(1, 16)
    sc.scrollok(True)
    sc.idlok(True)
    reset_supply(len(players))
    update_supply()

    if options['showdeck']:
        for i in range(2):
            statswin.append(curses.newwin(10, 30, 10+10*i, round(x*.75)))
            statswin[i].box()
            statswin[i].addstr(0, 2, 'stats')
            statswin[i].refresh()

    helpwin = curses.newwin(10, 30, 0, round(x*.75))
    helpwin.box()
    helpwin.addstr(0, 2, 'help')
    helpwin.refresh()

    handwin = curses.newwin(3, round(x*.5), 0,0)
    handwin.box()
    handwin.addstr(0, 2, 'hand')
    handwin.refresh()
    #handwin = curses.newwin(25, 30, 0, round(x*.5)+40)

    playwin = curses.newwin(3, round(x*.5), 3,0)
    playwin.box()
    playwin.addstr(0, 2, 'play')
    playwin.refresh()
    if set_opt is not None:
        options.update(set_opt)

    turn = 1
    #player1 = create_player(ai=smithy_big_money)
    #player2 = create_player(name='nic')

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
    update_stats()
    for p in players:
        if p['ai']:
            p['ai'].KINGDOM = card_costs
        shuffle(p['deck'])
        draw(p, 5)

    # show welcome message
    clear()
    console('WELCOME TO DOMINION')
    console('')
    console('OPTIONS:')
    console('Show deck:\t\t\t\t',options['showdeck'])
    console('Auto Play Treasures:\t\t\t',options['auto_play_treasures'])
    console('Skip Extra Buys On Less Than 2 Coins:\t',options['auto_skip_on_less_than_two_coins'])
    console('Kingdom Cards:',options['kingdom'])
    console('')
    console('PLAYERS:')
    for i in range(len(players)):
        console('Player',str(i+1) + ':',players[i]['name'])
    console('')
    if options['verbose']:
        #_blank = get_input('Press Return to start')
        wait_for_player()

    # game loop
    while turn < 100:
        clear()
        if turn == 1:
            turn_text = '1st'
        elif turn == 2:
            turn_text = '2nd'
        elif turn == 3:
            turn_text = '3rd'
        else:
            turn_text = str(turn) + 'th'
        for p in players:
            console(p['name']+"'s",turn_text,'turn')
            do_turn(p)
            #if not p['ai'] and options['verbose']:
            if options['verbose']:
                wait_for_player()
            if game_over():
                break
            console('')
        turn += 1
    #GAME IS OVER
    clear()
    console('The game has ended!')

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

    wait_for_player()

    if tie is not None:
        return len(players)
    return players.index(winner)

if __name__ == '__main__':
    curses.wrapper(game)
