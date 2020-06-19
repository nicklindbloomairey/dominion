#-------------------------------------------------------------------------------
# AI
#-------------------------------------------------------------------------------
NAME = 'ai_only_copper'

def ai_buy(s, me, coins=-1):
    return 'copper'

def ai_cellar_discard(s, me):
    for card in me['hand']:
        if get_card_type(card) == ['victory']:
            return card
    return 'done'

def ai_workshop(s, me):
    return 'copper'

def ai_remodel_gain(s, me, max_cost):
    return ai_buy(me, coins=max_cost)

def ai_remodel_trash(s, me):
    for card in ['estate', 'copper']:
        if card in me['hand']:
            return card
    return player['hand'][0]

def ai_mine(s, me):
    if 'silver' in me['hand']:
        return 'silver'
    return 'copper'

def ai_militia_discard(s, me):
    for card in ['estate', 'duchy', 'province']:
        if card in me['hand']:
            return card
    #find smallest cost card
    smallest = me['hand'][0]
    for card in me['hand']:
        if supply_costs[card] < supply_costs[smallest]:
            smallest = card
    return smallest
