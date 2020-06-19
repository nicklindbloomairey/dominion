import dominion
import smithy_big_money
import big_money

options = {'auto_play_treasures': True,
            'auto_skip_on_less_than_two_coins':True,
            'kingdom': ['cellar', 'moat', 'village',
            'merchant', 'workshop', 'smithy', 'remodel', 'militia', 'market',
            'mine'],
            'verbose': True}

dominion.game(smithy_big_money, 'nic', options)
