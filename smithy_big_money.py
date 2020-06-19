'''
Smithy Big Money

Buy silver, gold, province, duchy, estate and 1 smithy
'''
NAME = 'smithy_big_money'
KINGDOM = {}
value = {'copper':0, 'silver':3, 'gold':6, 'estate':2, 'duchy':5,
                'province':8, 'curse':0, 'smithy':7} # want smithy above gold

def ai_buy(s, me):

    #buy a smithy
    if me['turns'] in [1,2, 7, 8]:
        if me['coins'] in [4, 5]:
            return 'smithy'

    # base strategy
    if me['coins'] >= 8:
        cards = me['hand'] + me['deck'] + me['discard'] + me['play']
        golds = cards.count('gold')
        silvers = cards.count('silver')
        if golds == 0 and silvers < 5:
            return 'gold'
        return 'province'
    if me['coins'] in [6, 7]:
        if s['province'] <= 4:
            return 'duchy'
        return 'gold'
    if me['coins'] == 5:
        if s['province'] <= 5:
            return 'duchy'
        return 'silver'
    if me['coins'] in [3, 4]:
        if s['province'] <= 2:
            return 'estate'
        return 'silver'
    if me['coins'] == 2:
        if s['province'] <= 3:
            return 'estate'
    return 'done'

def ai_action(s, me):
    return 'smithy'

def ai_militia_discard(s, me):
    for card in ['estate', 'duchy', 'province']:
        if card in me['hand']:
            return card
    #find lowest value card
    smallest = me['hand'][0]
    for card in me['hand']:
        if value[card] < value[smallest]:
            smallest = card
    return smallest
