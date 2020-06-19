'''
ai.py

sample ai file

me = player object
me = {
        name: str,
        deck: list,
        hand: list,
        play: list,
        discard: list,
        actions: int,
        coins: int,
        buys: int,
        turns: int,
        vp: int
    }

KINGDOM is the cards in the supply and their costs
KINGDOM = {'copper':0, 'silver':3, ...}
It gets set by the game. Or set it yourself to show what
kingdom this ai is used to playing with.
'''
NAME = 'ai_name'
KINGDOM = {}


def ai_buy(s, me):
    ''' What do you want to buy?

    me - player object
    me['coins'] - how many coins we have
    '''
    return 'copper'

def ai_cellar_discard(s, me):
    ''' Which card do you want to discard from Cellar?

    This function will be called multiple times in sucesssion. Each time
    it needs the name of a card to discard. When done, respond with 'done'
    '''
    return 'done'

def ai_workshop(s, me):
    ''' What to gain from Workshop?
    '''
    return 'copper'

def ai_remodel_gain(s, me, max_cost):
    ''' What to gain from remodel?

    up to max_cost
    '''
    return 'copper'

def ai_remodel_trash(s, me):
    ''' What to trash for remodel?
    '''
    return me['hand'][0]

def ai_mine(s, me):
    ''' What to trash with mine?
    '''
    if 'silver' in me['hand']:
        return 'silver'
    return 'copper'

def ai_militia_discard(s, me):
    ''' When militia is played, what to discard?
    '''
    return me['hand'][0]
