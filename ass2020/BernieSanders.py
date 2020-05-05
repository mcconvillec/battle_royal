"""
Authors: Syndicate 13 
Calum McConville, Himansh Mishra, Stephanie Zhou, Rebecca Wang, Mia Wang
and Jason Yang

This module contains a class definition for Player, a class designed
to implement a score optimisation strategy for the Battle Royal game 
detailed in the Project Specification for the BUSA_90500_MAR Programming
subject.


Strategy:

- BernieSanders chooses to bide its time, moving and researching markets
  until it has information on at least 8 separate markets throughout 
  the map.
- Bernie tries to avoid debt by witholding a saving limit of $1000
- So long as Bernie has $2000 in the bank and there are enough turns
  to sell then Bernie will try to find a good market to buy at
- Late in the game or when Bernie has a low current_balance Bernie
  will find profitable markets to sell at
- Both the ranking of buying and selling markets is done by assessing markets
  based on the best available single buying or selling decision that can be
  taken at that market then prioritising markets that are close to Bernie 
  (done by optimise_decision and converge_solution functions). This is 
  done by placing a weight on the use of a turn and is designed to speed
  up Bernie's buying and selling
- If at any point there are no longer profitable markets to buy from
  or Bernie has finished selling then Bernie will move safely away from
  the black markets
- Bernie considers goals in sell_valuation function by choosing to 
  keep goal amount of an item if it is valued at less than $10,000
  on the market
"""


from collections import deque, defaultdict
from statistics import mean
import random
import numpy as np
from BasePlayer import BasePlayer
import Command

class Player(BasePlayer):
    """
    Player is designed to be called by the Game.py module and makes 
    buying, selling or movement decisions based on the 
    inputs to the take_turn method.
    """
    def __init__(self):
        #Instance variables that keep track of information throughout the game
        self.market_history = {} #combination of market research and info
        self.turn = 0 #turn counter
        self.inventory = defaultdict(int) #current player items and quantity in possession
        self.needs = None #unfulfilled amount of each goal
        self.savings = 1000 #gold buffer to protect from debt accrual
        self.current_balance = 0 #current gold balance of Player
        self.destination = [] #current planned destination of Player

    def dijkstra_lite(self, node_start, node_end, blackm, greym, short=False):
        """
        Author: Calum McConville
        This function is based off Dijkstra's algorithm implementation by Maria Boldyreva
        https://dev.to/mxl/dijkstras-algorithm-in-python-algorithms-for-beginners-dkc
        @param node_start starting node
        @param node_end ending/destination node
        @param blackm list of nodes that are black
        @param greym list of nodes that are grey 
        @returns a list of nodes within the map, containing the lowest cost path between nodes
        node_start and node_end
        """
        #Should impose penalty of 3 on black nodes and 2 on grey nodes along route
        grey_cost = 1.25
        black_cost = 1.5
        
        #tests whether node_end is a valid destination
        if node_end not in self.map.map_data['node_graph']:
            return False
        
        else:
            #set distance to inf for all nodes and 0 for current node
            distances = {vertex: float("inf") for vertex in self.map.map_data['node_graph'].keys()}
            distances[node_start] = 0

            #set all nodes as unvisited
            previous_vertices = {vertex: None for vertex in self.map.map_data['node_graph'].keys()}
            vertices = list(self.map.map_data['node_graph'].keys()).copy()

            while vertices:
                #select unvisited node with smallest distance as current position
                current_node = min(vertices, key=lambda vertex: (distances[vertex], vertex)) 

                #break if smallest distance among unvisited is infinity (something is wrong)
                if distances[current_node] == float("inf"):
                    break
                
                #checks the cost of moving to each of the nodes neighbouring the current node.
                for neighbour in self.map.map_data['node_graph'][current_node]:
                    if neighbour in blackm and not short:
                        alternative_route = distances[current_node] + black_cost
                    elif neighbour in greym and not short:
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
            
            path, current_node = deque(), node_end

            #generate path by moving through linked list to create path
            while previous_vertices[current_node] is not None:
                path.appendleft(current_node)
                current_node = previous_vertices[current_node]
            if path:
                path.appendleft(current_node)
            
            return list(path)

    def average_prices(self):
        """
        Author: Calum McConville
        Function returns the current average of all prices based on
        the most up-to-date information
        returns a dictionary with items as keys and average price as
        values
        """

        averages = defaultdict(list)
        
        #compiles all prices of items currently known
        for market in self.market_history:
            for item in self.market_history[market]:
                averages[item].append(self.market_history[market][item][0])
        
        #creates averages of each item based on current information
        averages = {k: mean(v) for k, v in averages.items()}
        return averages

    def predict_avg_quantity(self):
        """
        Authors: Rebeecca Wang, Mian Wang, Jason Yang and Stephanie Zhou
        Function returns the current average of all quantities based on
        the most up-to-date information

        returns a dictionary with items as keys and average quantity as
        values
        """

        predict_avg_qty = defaultdict(list)

        # compiles all quantities of items currently known
        for market in self.market_history:
            for item in self.market_history[market]:
                if self.market_history[market][item][1] is None:
                    pass
                else:
                    predict_avg_qty[item].append(self.market_history[market][item][1])

        # creates averages qty of each item based on current information
        predict_avg_qty = {k: int(mean(v)) for k, v in predict_avg_qty.items()}
        return predict_avg_qty

    def budget_amt(self, item, location, budget):
        """
        Author: Calum McConville
        Function returns the number of a particular item that 
        can be bought from a given store within a budget
        @param item the item being investigated
        @param location the market to buy from
        @param budget the amount of money we are willing to spend
        @returns the number of items that can be bought from the
        given market within a budget
        """
        
        #price of the item at given market
        price = self.market_history[location][item][0]
        
        return budget // price 

    
    def sell_valuation(self, market, decision_type=None):
        """
        Author: Calum McConville
        This function takes a market and returns the value of the best selling decision
        for that market. If decision_type == "sell" then this function returns the 
        selling decision to take

        @param market is the current market to consider
        @param decision_type is a flag that indicates the type of return value
        """

        best_return = 0
        for item in self.market_history[market]:
            #ONLY CONSIDERS SELLING STOCK ON TOP OF needs. CAN CHANGE THIS FOR TESTING
            #item_value = self.market_history[market][item][0] * (self.inventory[item] \
            #    - self.goal[item])
            item_value = self.market_history[market][item][0] * (self.inventory[item])

            if item_value > best_return:
                best_return = item_value
                if decision_type == "sell":
                    sell_item = item

        if decision_type == "sell" and best_return > 0: #BECAUSE OF 0 INVENTORY
            
            #Have we got enough in our inventory to reach our goal and is it profitable to keep them
            if (self.inventory[sell_item] > self.goal[sell_item] and self.needs[sell_item] > 0) \
            and self.goal[sell_item] * self.market_history[market][sell_item][0] < 10000:
                
                sell_amount = (self.inventory[sell_item] - self.goal[sell_item])
                #goal has been reached
                self.needs[sell_item] = 0
                #lock these items from selling
                self.inventory[sell_item] = 0

            else:
                sell_amount = self.inventory[sell_item]
                self.inventory[sell_item] -= sell_amount

            
            self.current_balance += (self.market_history[market][sell_item][0] \
             * sell_amount)

            return (sell_item, int(sell_amount))

        return best_return


    def market_item_buy_value(self, market, decision_type=None):
        """
        Authors: Rebecca Wang, Mia Wang, Jason Yang, Stephanie Zhou
        Function returns the best buy decision in this market based on
        the most up-to-date information

        @param market a name of a market to consider
        @param decision_type is a flag to determine the type of return value

        @returns an item name and quantity we can buy or the total revenue
        that is expected from this buying decision (if decision_type is None)
        """

        best_item = ''
        best_value = 0
        purchase_qty = None

        for item in self.market_history[market]:

            budget_amt = self.budget_amt(item, market, self.current_balance)

            if self.market_history[market][item][1] is not None:
                qty = min(budget_amt, self.market_history[market][item][1])
                item_value = (self.average_prices()[item] \
                 - self.market_history[market][item][0]) * qty

            else:
                qty = min(budget_amt, int(self.predict_avg_quantity()[item]))
                item_value = (self.average_prices()[item] \
                 - self.market_history[market][item][0]) * qty

            if item_value > best_value:
                best_item = item
                best_value = item_value
                purchase_qty = qty

        if purchase_qty and decision_type == "buy":
            self.inventory[best_item] += purchase_qty
            self.current_balance -= purchase_qty \
            * self.market_history[market][best_item][0]
            return (best_item, int(purchase_qty))
        
        #Either there is no stock or we just want to rank market
        return best_value

    def optimise_decision(self, helper_function, location, bm, gm):
        """
        Author: Calum McConville
        This function takes a helper function and ranks markets based on the outcome
        of that helper function

        @param helper_function takes a market and ranks it based on buying or selling 
        profit
        @param location the current location of the player
        @param bm current black_markets in the game
        @param gm current grey_markets in the game

        @returns the expected profit from the current location either for selling or
        buying
        """
        turn_max = defaultdict(tuple)
        #find optimum selling decisions for each turn
        for market in self.market_history:
            #Returns the shortest path to this market from current location
            path = len(self.dijkstra_lite(location, market, bm, gm))
            radius = max(0, path - 1) #incase we're considering current location
                    
            #If this is the only market that takes this turn
            if not radius in turn_max:
                turn_max[radius] = (helper_function(market), market)
                    
            else:
                market_sell = helper_function(market)
                #If this is the most profitable market with equivalent distance
                if market_sell > turn_max[radius][0]:
                    turn_max[radius] = (market_sell, market)

        return turn_max


    def move_safely(self, location, bm, gm):
        """
        Authors: Jason Yang, Stephanie Zhou, Calum McConville
        Function calculates the most efficient route for the player to take
        to stay out of black zone

        @param location is the current market location being considered
        @param bm is a list of black markets
        @param gm is a list of grey markets
        @return a move option to either move towards safe zone or stay in safe zone.
        """

        safe_neighbours = list(np.setdiff1d(list(self.map.get_neighbours(location)), bm + gm))

        if location not in gm + bm:
            return None
        elif safe_neighbours:
            return safe_neighbours[random.randint(0, len(safe_neighbours) - 1)]
        else:
            distance = 0
            for market in list(np.setdiff1d(list(self.map.map_data['node_graph'].keys()), bm + gm)):
                travel_time = list(self.dijkstra_lite(location, market, bm, gm, short=True))[1:]
                if  len(travel_time) < distance:
                    distance = len(travel_time)
            #move to suggested destination
            return travel_time[0]


    def converge_solution(self, turn_max, turn_value):
        """
        Author: Himansh Mishra and Calum McConville
        Function evaluates and chooses best buying and selling locations based on distances 
        from current location
        @param turn_max: Dictionary that lists best market for each distance from current location
        @param turn_value: The associated value placed on a single turn
        
        @returns tuple containing the target location and expected profits
        """
        if 0 not in turn_max:
            # we haven't researched current location
            current_solution = (0, None)

        else:
            current_solution = turn_max[0]

        for n_turn in turn_max:
            #Choose most profitable decision when considering turn penalty to get to destination
            if current_solution[0] < turn_max[n_turn][0] - (n_turn * turn_value):
                current_solution = (turn_max[n_turn][0] - (n_turn * turn_value), \
                    turn_max[n_turn][1])

        return current_solution

    def take_turn(self, location, prices, info, bm, gm):
        """
        @param location Name of your current location on map as a str.
        @param prices A dictionary {product:(price,amount)} of prices and amounts 
        at this market (if you have researched, {} otherwise).
        @param info A dictionary {market:{product:price}} of information gleaned from other 
        players that were here when you arrived.
        @param bm A list of market names (strings) that are Black.
        @param gm A list of market names (strings) that are Grey.
        @returns (cmd, data) cmd is one of Command.* and data is a tuple of 
        necessary data for a command or None.
        """

        assert isinstance(location, str)
        assert isinstance(prices, dict)
        assert isinstance(info, dict)
        
        #Keep track of the stage of the game
        self.turn += 1

        #initialise self.need and self.current_balance at game start
        if self.turn == 1:
            self.needs = self.goal.copy()
            #create buffer amount to prevent accruing debt
            self.current_balance = self.gold - self.savings 

        #Keep track of gold based on black market penalty
        if location in bm:
            self.current_balance -= 100

        #Keep track of gold based on interest payments
        if self.current_balance < 0:
            self.current_balance -= self.current_balance * 0.10
        
        #Update market_history based on new information or prices received
        if info:
            for market in info:
                #as long as we don't already have the market information
                if market not in self.market_history:
                    self.market_history[market] = \
                    {k: (v, None) for (k, v) in info[market].items()}

        if prices:
            #Uses prices to update or add information stored in market_history
            self.market_history[location] = prices


        #We have minimal information and should try to gain more knowledge on markets
        if len(self.market_history) < 8:

            #If we have researched the market move on, avoiding black and grey markets
            if prices:
                options = [x for x in list(self.map.get_neighbours(location)) \
                if x not in bm + gm]
                
                return (Command.MOVE_TO, options[random.randint(0, len(options) - 1)])
            
            #If we haven't researched the market, research
            else:
                return (Command.RESEARCH, None)

        #Start optimising buying and selling based on stored market information
        elif len(self.market_history) >= 8:

            #We are not currently executing a strategy
            if not self.destination:
               
                #Enough gold and right stage of game to buy
                if self.current_balance > 2000 and self.turn < 280:

                    #Weighting placed on the use of a turn
                    turn_value = 100 + (0.5 * self.turn)

                    #Returns the maximum expected buying return by distance from location
                    turn_max = self.optimise_decision(self.market_item_buy_value, \
                        location, bm, gm)

                    #Return optimal buying market considering turn usage penalty
                    current_solution = self.converge_solution(turn_max, turn_value)

                    #If there are no profitable buying markets
                    if not current_solution[1]:
                        next_step = self.move_safely(location, bm, gm)
                        if next_step:
                            return (Command.MOVE_TO, str(next_step))
                        else:
                            return (Command.PASS, None)

                    #Our current market is our most profitable
                    elif current_solution[1] == location:
                        
                        if prices:
                            self.destination = []

                            #Calculate best buying decision at current location
                            decision = self.market_item_buy_value(location, decision_type="buy")
                            
                            #There was no profitable buy opportunity
                            if isinstance(decision, int):
                                return (Command.PASS, None)

                            return (Command.BUY, decision)
                        
                        else:                            
                            return (Command.RESEARCH, None)
                    
                    else:
                        #Set current destination to suggested market with intention to buy
                        self.destination = list(self.dijkstra_lite(location, current_solution[1], \
                         bm, gm))[1:] + ['buy']
                        #start moving to best buying market
                        next_step = self.destination.pop(0)
                        return (Command.MOVE_TO, next_step)

                elif sum([v for k, v in self.inventory.items()]) != 0:
                    turn_value = 100
                    #Returns the maximum expected selling return by distance from location
                    turn_max = self.optimise_decision(self.sell_valuation, \
                        location, bm, gm)
                    
                    #Return optimal selling market considering turn usage penalty
                    current_solution = self.converge_solution(turn_max, turn_value)

                    #If current market is optimal
                    if current_solution[1] == location or current_solution[1] is None:
                        if prices:

                            decision = self.sell_valuation(location, decision_type="sell")
                            
                            #If no profitable selling option found
                            if isinstance(decision, int):
                                return (Command.PASS, None)

                            return (Command.SELL, decision)
                        
                        else:                            
                            return (Command.RESEARCH, None)
                    else:
                        #set destination to best selling market with intention to sell
                        self.destination = list(self.dijkstra_lite(location, current_solution[1] \
                            , bm, gm))[1:] + ['sell']
                        #move to destination
                        next_step = self.destination.pop(0)
                        return (Command.MOVE_TO, next_step)

                else:
                    #We do not have inventory to sell and should stay safe
                    next_step = self.move_safely(location, bm, gm)
                    if next_step:
                        return (Command.MOVE_TO, str(next_step))
                    else:
                        return (Command.PASS, None)
            
            
            else:
                #Execute current strategy 
                if self.destination == ['sell']:
                    #we've arrived at selling location and should assess options
                    if prices:
                        self.destination = []
                        decision = self.sell_valuation(location, decision_type="sell")
                        
                        if isinstance(decision, int):
                            return (Command.PASS, None)
                        
                        return (Command.SELL, decision)
                    
                    else:
                        return (Command.RESEARCH, None)

                elif self.destination == ["buy"]:
                    #we've arrived at buying location and should assess options
                    if prices:
                        self.destination = []
                        decision = self.market_item_buy_value(location, decision_type="buy") 
                        
                        if isinstance(decision, int):
                            return (Command.PASS, None)

                        return (Command.BUY, decision)
                    
                    else:
                        return (Command.RESEARCH, None)

                else:
                    #Still en-route, keep moving
                    next_step = self.destination.pop(0)
                    return (Command.MOVE_TO, next_step)
