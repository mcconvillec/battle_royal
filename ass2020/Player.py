from BasePlayer import BasePlayer
import Command
from collections import deque, defaultdict



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
- Can I write a function that takes two nodes and returns a list of nodes that represents the shortest path between them?



IMPORTANT DECISIONS:
- If to research (done but need to also consider black or grey)
- If to buy #prices, inventory, gold, goal
- If to sell
- If to move
- Where to move

Of all the information we have:
- Calculate the profit we can make at each market and how many turns it will take to realise that profit
- Decide based on amount of profit/number of turns which market to travel to
- Perfect market is where we can sell our other items high and also then stock up on goal items
"""


class Player(BasePlayer):


    def __init__(self):
        #Instance variables that keep track of information throughout the game

        self.market_history = {} #combination of market research and info
        self.turn_num = 0
        self.inventory = {} #current player items and quantity in possession

    def dijkstra_lite(self, n1, n2, blackm, greym):
        """
        Author: Calum McConville

        This function is based off Dijkstra's algorithm implementation by Maria Boldyreva
        https://dev.to/mxl/dijkstras-algorithm-in-python-algorithms-for-beginners-dkc

        @param n1 starting node
        @param n2 ending/destination node
        @param blackm list of nodes that are black
        @param greym list of nodes that are grey 

        @returns a list of nodes within the map, containing the lowest cost path between nodes
        n1 and n2
        """
        #Sould impose penalty of 3 on black nodes and 2 on grey nodes
        grey_cost = 2
        black_cost = 3
        
        #tests whether n2 is a valid destination
        if n2 not in self.map.map_data['node_graph']:
            return False
        
        else:
            #set distance to inf for all nodes and 0 for current node
            distances = {vertex: float("inf") for vertex in self.map.map_data['node_graph'].keys()}
            distances[n1] = 0

            #set all nodes as unvisited
            previous_vertices = {vertex: None for vertex in self.map.map_data['node_graph'].keys()}
            vertices = list(self.map.map_data['node_graph'].keys()).copy()

            while vertices:
                #select unvisited node with smallest distance as current position
                current_node = min(vertices, key = lambda vertex: (distances[vertex], vertex)) 
                print(f"current node = {current_node}")

                #break if smallest distance among unvisited is infinity (something is wrong)
                if distances[current_node] == float("inf"):
                    break
                
                """
                checks the cost of moving to each of the nodes neighbouring the current node.
                Nodes that are either black or grey receive an additional penalty
                """
                for neighbour in self.map.map_data['node_graph'][current_node]:
                    print(f"neighbour = {neighbour}")
                    if neighbour in blackm:
                        alternative_route = distances[current_node] + black_cost
                    elif neighbour in greym:
                        alternative_route = distances[current_node] + grey_cost
                    else:
                        alternative_route = distances[current_node] + 1

                    #check if this is currently the fastest way to reach the neighbour
                    if alternative_route < distances[neighbour]:
                        distances[neighbour] = alternative_route
                        #if we've discovered a new fastest route update the access node
                        previous_vertices[neighbour] = current_node
                
                #Remove current node from unvisited nodes
                vertices.remove(current_node)
            
            path, current_node = deque(), n2

            #generate path by moving through linked list to create path
            while previous_vertices[current_node] is not None:
                path.appendleft(current_node)
                current_node = previous_vertices[current_node]
            if path:
                path.appendleft(current_node)
                return path
    """
    def estimate_profit(self, market, turns):
       
        #Author: Calum McConville
        #@param market is the market we want to evaluate

        #@returns (turns, profit, market) profit is the maximum amount we can generate from market and turns
        #is the number of turns this will take
        

        #profit = price we could sell our inventory + time it takes to get there 
        market_prices = self.market_history[market]

        expected_profit = []
        for item in market_prices:
            expected profit = expected
    """



    def take_turn(self, location, prices, info, bm, gm):
        """
        @param location Name of your current location on map as a str.
        @param prices A dictionary {product:(price,amount)} of prices and amounts 
        at this market (if you have researched, {} otherwise).
        @param info A dictionary {market:{product:price}} of information gleaned from other 
        players that were here when you arrived.
        @param bm A list of market names (strings) that are Black.
        @param gm A list of market names (strings) that are Grey.

        @returns (cmd, data) cmd is one of Command.* and data is a tuple of necessary data for a command or None.
        """
        
        #return (Command.PASS, None)
        assert(type(location) is str)
        assert(type(prices) is dict)
        assert(type(info) is dict)
        
        #keep track of the stage of the game
        self.turn_num += 1
        
        #Always add any new information from other players to market_history in same format as prices
        if info:
            print("we made it")
            #NEED TO CHANGE THIS
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

            #move towards c
            path = self.dijkstra_lite(location, 'c', bm, gm)
            print(path)
            return (Command.MOVE_TO, path[1])

        elif self.market_history:
            """
            We have not researched the current market and need to decide if its
            worth the turn required to research.
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
                #see how much money we can generate in 1,2,3,4,5,6,7 turns

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

    


 

#self.map.get_neighbours(node_name)

#self.map.is_road(n1, n2)


