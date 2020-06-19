'''
Big Money

Buy silver, gold, province, duchy, estate
'''
NAME = 'big_money'
KINGDOM = {}
value = {'copper':0, 'silver':3, 'gold':6}

def ai_buy(s, me):

    if me['coins'] >= 8:
        cards = me['hand'] + me['deck'] + me['discard'] + me['play']
        golds = cards.count('gold')
        silvers = cards.count('silver')
        if golds == 0 and silvers < 5:
            return 'gold'
        return 'province'
    if me['coins'] >= 6:
        if s['province'] <= 4:
            return 'duchy'
        return 'gold'
    if me['coins'] >= 5:
        if s['province'] <= 5:
            return 'duchy'
        return 'silver'
    if me['coins'] >= 3:
        if s['province'] <= 2:
            return 'estate'
        return 'silver'
    if me['coins'] >= 2:
        if s['province'] <= 3:
            return 'estate'
    return 'done'

def ai_militia_discard(s, me):
    for card in ['estate', 'duchy', 'province', 'curse']:
        if card in me['hand']:
            return card
    #find smallest cost card
    smallest = me['hand'][0]
    for card in me['hand']:
        if value[card] < value[smallest]:
            smallest = card
    return smallest
