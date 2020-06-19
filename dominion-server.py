''' dominion_server.py

Sections of file:
      - OPTIONS
      - CONSTANTS
      - GLOBALS
      - ACTION CARD FUNTIONS
      - CURSES FUNCTIONS
      - GAME HELPER FUNTIONS
      - main()

player dict format
    name: player name
    ai: the namespace containing the ai functions
    id: #unique player id (player 1, player 2, ...
    deck: list of cards
    hand: list of cards
    play: list of cards
    discard: list of cards
    actions: int
    coins: int
    buys: int
    turns: how many turns this player has actually finished (different from game turns)
    vp: int 

Game state dict format
    players: list of player dicts
    supply_piles: map [card name] -> [amount left in pile]
    trash_pile: list of cards
    turn: the current turn number

dominion protocol:

    client -> server
        pack entire game state and send it

    server -> client
        pack entire game state and send it
'''
# 128 x 30
# stand alone helper functions
# ex: costs(card) returns cost of a card
from helper import *

import curses
import curses.textpad
import smithy_big_money
import big_money
import sys
import socket
import selectors
import traceback
import struct
import json
import io

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
# CONSTANTS
#-------------------------------------------------------------------------------
MAX_TURNS = 100

R = selectors.EVENT_READ
W = selectors.EVENT_WRITE
RW = selectors.EVENT_READ | selectors.EVENT_WRITE

#-------------------------------------------------------------------------------
# GLOBALS
#-------------------------------------------------------------------------------
# HOLDS ALL GAME STATE -- I trust everything
# if a function edits this, it will have "global game"
game = {
    "player_list": [], # created by create_player() 
    "supply_piles": {}, # set up in reset_supply()
    "trash_pile": [],
    "turn": 0
}

line = 1 # the line number of the console info to be printed onto next

#windows
stdscr = None #console area
supply = None # supply amounts
handwin = None # hand window
playwin = None # play window
helpwin = None # help text window
statswin = [] # deck list windows

#networking

sel = selectors.DefaultSelector()

clients = {}
recv_buffer = b""
msglen = None

#-------------------------------------------------------------------------------
# NETWORKING FUNCTIONS
#-------------------------------------------------------------------------------
def _json_encode(obj, encoding):
    return json.dumps(obj, ensure_ascii=False).encode(encoding)

def _json_decode(json_bytes, encoding):
    tiow = io.TextIOWrapper(
        io.BytesIO(json_bytes), encoding=encoding, newline=""
    )
    obj = json.load(tiow)
    tiow.close()
    return obj

def write(socket, data):
    send_buffer = data

    if send_buffer:
        #print("sending", repr(send_buffer), "to", clients[socket])
        try:
            # Should be ready to write
            sent = socket.send(send_buffer)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            send_buffer = send_buffer[sent:] #update the send buffer
            sel.modify(socket, RW, data=send_buffer)

    if not send_buffer:
        # Set selector to listen for read events, we're done writing.
        sel.modify(socket, R)
        message_queued = False

def broadcast(msg):
    json_message = _json_encode(msg, "utf-8")
    message_hdr = struct.pack(">H", len(json_message))
    message = message_hdr + json_message
    for client in list(clients):
        sel.modify(client, RW, data=message)
    return


def read(socket):
    global recv_buffer
    global msglen

    try:
        # Should be ready to read
        data = socket.recv(4096)
    except BlockingIOError:
        # Resource temporarily unavailable (errno EWOULDBLOCK)
        pass
    else:
        if data:
            recv_buffer += data
        else:
            raise RuntimeError("Peer closed.")

    if msglen is None:
        hdrlen = 2
        if len(recv_buffer) >= hdrlen: #proto header has arrived
            msglen = struct.unpack(
                ">H", recv_buffer[:hdrlen]
            )[0]
            recv_buffer = recv_buffer[hdrlen:]

    if msglen is not None:
        if len(recv_buffer) >= msglen: #json message arrived
            message = _json_decode(
                recv_buffer[:msglen], "utf-8"
            )
            recv_buffer = recv_buffer[msglen:]
            msglen = None
            if message['message'] == 'join_message':
                print(message['user'],'joined the server from',clients[socket]['addr'])
                clients[socket]['name'] = message['user']
            else:
                print(message['user'],'>',message['message'])
            broadcast(message)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    #print("accepted connection from", addr)
    conn.setblocking(False)
    clients[conn] = {}
    clients[conn]['addr'] = addr
    sel.register(conn, selectors.EVENT_READ)

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
    global game # players need to discard
    console('ATTACK:',player['name'],'played a militia!')
    player['coins'] += 2

    #force other players to discard
    for other_player in game["player_list"]:
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
# CURSES FUNCTIONS
#-------------------------------------------------------------------------------
def curses_setup(stdscr_arg):
    global stdscr
    global supply
    global handwin
    global playwin
    global helpwin
    global statsp1
    global statsp2

    # make screen global
    stdscr = stdscr_arg
    # CURSES setup
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    y, x = stdscr.getmaxyx()
    stdscr.resize(y-6, round(x/2))
    stdscr.mvwin(6,0)
    supply = curses.newwin(len(card_costs)+3, 30, 0,round(x/2))
    stdscr.setscrreg(1, 16)
    stdscr.scrollok(True)
    stdscr.idlok(True)
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

    playwin = curses.newwin(3, round(x*.5), 3,0)
    playwin.box()
    playwin.addstr(0, 2, 'play')
    playwin.refresh()
    update_stats()
    return

def console(*text):
    ''' same as print(text) but for the curses implementation
    it adds a line of text to the console info area, scrolling if needed
    '''
    global line
    global stdscr
    if not options['verbose']:
        return
    #print(*text)
    if line >= 16:
        stdscr.addstr(16, 1,''.join([str(x)+' ' for x in text])) 
        stdscr.scroll()
    else:
        stdscr.addstr(line, 1,''.join([str(x)+' ' for x in text])) 
    stdscr.clrtoeol()
    stdscr.box()
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
    stdscr.erase()
    stdscr.box()
    stdscr.addstr(22,1,'type "help [card]" for that cards text')
    stdscr.refresh()
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

def print_hand(player):
    ''' update hand window '''
    global handwin
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
    global playwin
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
    stdscr.addstr(y-2-6, x-1, prompt)
    stdscr.clrtoeol()
    stdscr.box()
    #make a text box
    win = curses.newwin(h, w, y, x)
    # draw a nice rectangle around text box
    curses.textpad.rectangle(stdscr, y-1-6, x-1, y+h-6, x+w)
    stdscr.refresh()
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
        stdscr.move(i, 0)
        stdscr.clrtoeol()
    stdscr.box()
    
    stdscr.refresh()
    return text

def wait_for_player():
    ''' waits for player to press a key until continuing '''
    stdscr.addstr(25-2-6, 2-1, 'press any key to continue')
    stdscr.clrtoeol()
    stdscr.box()
    stdscr.refresh()
    # needs to be in delay mode
    stdscr.getkey() # this pauses the program, we dont do anything with the keypress
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

#-------------------------------------------------------------------------------
# GAME HELPER FUNCTIONS
#-------------------------------------------------------------------------------
def reset_supply(n=2):
    ''' resets the supply amounts
    n - number of players
    '''
    global game
    estate_and_duchy = {2:8, 3:12, 4:12, 5:12, 6:12}
    curse = (n-1)*10
    province = {2:8, 3:12, 4:12, 5:15, 6:18}
    supply_num = {'copper':60,'silver':40,'gold':30,'estate':estate_and_duchy[n],
        'duchy':estate_and_duchy[n],'province':province[n],'curse':curse}
    for card in kingdom:
        supply_num[card] = 10
    game["supply_piles"] = supply_num
    return


def trash(player, card):
    ''' "trash" events go here?
    '''
    global game
    player['hand'].remove(card)
    game["trash_pile"].append(card)
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
    global game
    if supply_num[card] < 1:
        console('there are no',card,'left')
        return
    if dest is not 'discard':
        console('you gain',a(card),'to your',dest)
    else:
        console('you gain',a(card))
    game["supply_piles"][card] -= 1
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


def game_over():
    ''' check if the game is over, return true or false 
    accesses game state
    '''
    if game["supply_piles"]['province'] < 1: # no provinces left
        return True
    count_empty = sum(1 if game["supply_piles"][card] < 1 else 0 for card in game["supply_piles"])
    if count_empty >= 3:
        return True
    return False

def create_player(name='player',ai=None):
    ''' returns a player dictionary with a starting deck and pointers to the
    ai if the player is an ai
    accesses game state for number of players
    '''
    # basic player object
    player = {
        "name": ai.NAME if ai else name,
        "ai": ai, # should be a namespace containing the ai functions
        "id": len(game["player_list"])+1, #unique player id
        "deck": create_start_deck(),
        "hand": [],
        "play": [],
        "discard": [],
        "actions": 0,
        "coins": 0,
        "buys": 0,
        "turns": 0,
        "vp": 0,
    }

    return player

def find_winner():
    ''' returns a list of winning players
    if list is only one element, we have a sole winner,
    otherwise the winner list is the list of players that tied for win
    '''
    global game
    winner = [game["player_list"][0]] #let first player be winner
    for p in game["player_list"]:
        if p in winner:
            continue
        if p['vp'] > winner['vp']:
            winner = [p] #new winner
        elif p['vp'] == winner['vp']:
            if p['turns'] < winner['turns']:
                # p beats winner in tie breaker
                winner = [p] 
            elif p['turns'] == winner['turns']:
                # p tied winner
                winner.append(p)

    return winner

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
def main(stdscr, p1=None, p2=None, set_opt=None):
    ''' runs the game
    game settings passed in as options or uses default

    arguments:
        stdscr - curses main screen given to us by curses.wrapper(main)
    '''
    global options
    global game
    #update the options
    if set_opt is not None:
        options.update(set_opt)
    # create players
    for name, ai in options['players']:
        game["player_list"].append(create_player(name, ai)) 
    reset_supply(len(game["player_list"]))

    curses_setup(stdscr)

    game["turn"] = 1
    for p in game["player_list"]:
        if p['ai']:
            p['ai'].KINGDOM = card_costs # tell ai about the kingdom costs
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
    for i in range(len(game["player_list"])):
        console('Player',str(i+1) + ':',game["player_list"][i]['name'])
    console('')
    if options['verbose']:
        #_blank = get_input('Press Return to start')
        wait_for_player()

    # game loop
    while game["turn"] < MAX_TURNS:
        clear()
        if turn == 1:
            turn_text = '1st'
        elif turn == 2:
            turn_text = '2nd'
        elif turn == 3:
            turn_text = '3rd'
        else:
            turn_text = str(turn) + 'th'
        for p in game["player_list"]:
            console(p['name']+"'s",turn_text,'turn')
            do_turn(p)
            #if not p['ai'] and options['verbose']:
            if options['verbose']:
                wait_for_player()
            if game_over():
                break
            console('')
        game["turn"] += 1
    #GAME IS OVER
    clear()
    console('The game has ended!')

    for p in game["player_list"]:
        p['vp'] = count_vp(p)
        console(p['name'],'has',p['vp'],'victory points','and had',p['turns'],'turns')

    # find winner
    winner = find_winner()

    #print who won
    if len(winner) == 1:
        console(winner['name'],'won the game!')
    else: #tie
        tied_players = [winner[0]["name"]]
        for i in range(1, len(winner)):
            tied_players.append('and')
            tied_players.append(winner[i]["name"])
        console(tied_players,'tied!')

    wait_for_player()

#-------------------------------------------------------------------------------
# SCRIPT START
#-------------------------------------------------------------------------------

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ)

try:
    while True:
        events = sel.select(timeout=1) #blocking
        for key, mask in events:
            if key.fileobj is lsock: #new connection
                accept_wrapper(key.fileobj)
                continue
            sock = key.fileobj
            data = key.data
            try:
                if mask & selectors.EVENT_READ:
                    read(sock)
                if mask & selectors.EVENT_WRITE:
                    write(sock, data)
            except Exception:
                print(
                    "main: error: exception for",
                    f"{clients[sock]['addr']}:\n{traceback.format_exc()}",
                )
                exit()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
