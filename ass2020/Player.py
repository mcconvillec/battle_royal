from BasePlayer import BasePlayer
import Command

class Player(BasePlayer):
	"""Minimal player."""
	def take_turn(self, location, prices, info, bm, gm):
		return (Command.PASS, None)