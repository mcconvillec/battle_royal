# Battle Royal
Python class-based solution to creating a player to compete in fictional battle_royal game

# Description:

- ass2020/BernieSanders.py: Final player that implements buying and selling strategy to maximise profit
- take_turn method withing Player class returns:
     1) (MOVE_TO, 'char') to navigate nodes in a map
     2) (BUY or SELL, ('product', qty)) to trade at markets
     3) (PASS, None) to void turn

Inputs: Each turn
- String name of current location
- Market inventory (if researched): {product: (price, amount), product2: (price,amount)}
- Market inventory (if no research): {}
- Player information: {market1: {product: price, product2: price}, market2: {product1: price, product2:price}}
- Black: [“market1”, “market2”, “market3”]
- Grey: [“market1”, “market2”, “market3”]


