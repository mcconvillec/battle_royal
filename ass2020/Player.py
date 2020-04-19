from BasePlayer import BasePlayer
import Command
from collections import defaultdict


"""
IDEAS:

Buying:
- If price of an item at a store is < average of all items or in x percentile of prices for that same
  item that we have seen previously or from other players we buy as much as possible (or based on
  what quantile it is in) and if store we would want to sell it isn't in black or grey. Need to now
  store that we're heading for a given store or one of the stores that is close
- Some weighting on how close to our target an item would get us and how good the price is
- If we can buy enough to reach our target and the amount required to buy is > 10,000 then we buy (
  based slightly on prices)
- If we can overdraw but get to our goal AND we have extra items in stock that sell for more than overdraw,
  go into debt
- Sell the most valuable product categories that don't threaten goals when turn > 48, also don't buy new items late in game


    #Decide whether to purchase items at the current market
        #-Could we profit from buying items?
        #      - Will we enter black zone by buying and is it worth the turn?
        #-How much money do we have to spend?
        #-How long is left in the game to sell what we have?

Movement:
- Conservative: leave as soon as Grey
- Risky: If expected return off market is >100 stay (based on known prices of sale and buy prices or reaching goal)



IMPORTANT DECISIONS:
- If to research (done but need to also consider black or grey)
- If to buy 
- If to sell
- If to move
- Where to move
"""


class Player(BasePlayer):
    """Minimal player."""

    #can we store:
    #1) Turn number
    #2) All the prices of markets we have researched
    #3) All the information we have seen from other players previously
    #4) Our gold
    #5) Our current inventory
    """@param loc Name of your current location on map as a str.
           @param this_market A dictionary {product:(price,amount)} of prices and amounts 
                              at this market (if you have researched, {} otherwise).
           @param info A dictionary {market:{product:price}} of information gleaned from other 
                       players that were here when you arrived.
           @param black_markets A list of market names (strings) that are Black.
           @param grey_markets A list of market names (strings) that are Grey.

           @return (cmd, data) cmd is one of Command.* and data is a tuple of necessary data for a command.
    """

    def take_turn(self, location, prices, info, bm, gm):
        #return (Command.PASS, None)
        assert(type(location) is str)
        assert(type(prices) is dict)
        assert(type(info) is dict)
        
        self.turn_num += 1

        #Always add any new information from other players to market_history in same format as prices
        if info:
            for market in info:
                #as long as we don't already have the market information
                if market not in self.market_history:
                    self.market_history[market] = \
                    {market: {k: (v, None)} for (k, v) in info[market].items()}
        

        if prices:
            """
            We have researched the market and want to decide whether to buy
            or sell
            """

            #Uses prices to update or add information stored in market_history
            self.market_history[location] = prices
            return (Command.PASS, None)

        elif self.market_history:
            """
            We have not researched the current market and need to decide if its
            worth the tur required to research.

            We also have no information about other markets this turn
            """
            if location in self.market_history:
                #i.e. we have information about this market from other players
                
                market_avg = defaultdict(list)
                #compute average prices function:
                for loc in self.market_history:
                    for prod in self.market_history[loc]:
                        #keep track of the price of all products
                        market_avg[prod].append(self.market_history[loc][prod][0])

                #check if this market has stock of goal items or price competitive items.
                for product in self.market_history[location]:
                    #check if prices in this market are competitive with other prices
                    if self.market_history[location][product][0] <= mean(market_avg[product]) and self.turn_num <= 45:
                        return (Command.RESEARCH, None)
                    
                    #check if there are goal items and if we've met our goal
                    elif product in goal and (self.inventory and self.inventory[product] < self.goal[product]):
                        return (Command.RESEARCH, None)
                    

                #didn't find any low price items or goal items
                #assess where we should move


            else:
                return (Command.PASS, None)
                #we have no information about this location
                if location in gm:
                    #location is grey, so researching would put us in black
                    #assess where we can move to and move away from black
                    pass
                elif location in bm:
                    #probably try and get out
                    pass
        else:
            #WE HAVE NO INFORMATION ABOUT ANY MARKETS IN THE GAME
            return (Command.RESEARCH, None)

    #def analyse_market(self):
        """
        Computes the average price of all products we currently have information about
        """


 

#self.map.get_neighbours(node_name)

#self.map.is_road(n1, n2)


