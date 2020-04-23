from Game import Game_old
from Player2 import Player

import sys

if len(sys.argv) != 2:
	print("Usage: {} bool".format(sys.argv[0]))
else:
	verb = sys.argv[1]

	p1 = Player()
	p2 = Player()

	g = Game([p1,p2], verbose = verb)

	res = g.run_game()

	print(res)