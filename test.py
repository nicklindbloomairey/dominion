import dominion
import time
import sys
import big_money
import smithy_big_money
import ai_only_copper

#ai = [sys.argv[2], sys.argv[3]]
ai = [smithy_big_money, big_money]

n = int(sys.argv[1])
wins = [0, 0, 0]

t0 = time.time()
for i in range(n):
    wins[dominion.game(ai[0], ai[1])] += 1
t1 = time.time()
print(n,'games took',round(t1-t0, 1),'seconds')
percent = [round((x/n)*100,2) for x in wins]
for i in range(2):
    print(ai[i].NAME,'won',str(percent[i]) + '% of games')
print('they tied',str(percent[2]) + '% of games')
