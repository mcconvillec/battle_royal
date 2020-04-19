from BasePlayer import BasePlayer
import Command






class Benchmark(BasePlayer):
	"""Minimal player."""
	def take_turn(self, location, prices, info, bm, gm):
		#self.turn_num += 1
		#print("Turn number is %d"%self.turn_num)
		return (Command.PASS, None)