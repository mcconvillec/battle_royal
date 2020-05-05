"""
Authors: Syndicate 13 
Calum McConville, Himansh Mishra, Stephanie Zhou, Rebecca Wang, Mia Wang
and Jason Yang

This module contains a class definition for Player, a program designed
to implement a score optimisation strategy for the Battle Royal game 
detailed in the Project Specification for the BUSA_90500_MAR Programming
subject.
"""


from collections import deque, defaultdict
import random
from statistics import mean
from BasePlayer import BasePlayer
import Command


#ISSUES TO FIX:
#Think about when we want:
# focus on getting goals,
#Make estimate quantity and price one function with (index = 1 or 0 argument)
#Figure out what is happening with Himansh's function and get rid of ranking by location if it doesn't work
# run away and avoid black 
# ifelse buy return off current market <= 0 (in Rebecca's function) then Command.Pass
#ERRORS:
#-Try different weightings on turns (INCREASED MIGHT SPEED UP ACTIONS)
#-Try different levels of info before optimising (10, 5, less than 5?)



class Player(BasePlayer):
    """
    Player class is a subclass of the BasePlayer class. Player
    is designed to be called by the Game.py module and makes 
    buying, selling or movement decisions based on the 
    inputs to the take_turn method.
    """
    def __init__(self):
        #Instance variables that keep track of information throughout the game
        self.market_history = {} #combination of market research and info
        self.turn = 0
        self.inventory = defaultdict(int) #current player items and quantity in possession
        self.needs = None #will store achievable goal
        self.savings = 1000
        self.current_balance = 0 #current gold balance of Player
        self.destination = [] #current planned destination of Player

    def dijkstra_lite(self, node_start, node_end, blackm, greym):
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
        #Sould impose penalty of 3 on black nodes and 2 on grey nodes
        grey_cost = 2
        black_cost = 3
        
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
        Authors: Rebeecca Wang and Mia Wang
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

    
    def value_inventory(self, market, decision_type=None):
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
            #sell_amount = (self.inventory[item] - self.goal[item])
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
                qty = min(budget_amt, self.predict_avg_quantity()[item])
                item_value = (self.average_prices()[item] \
                 - self.market_history[market][item][0]) * qty

            if best_value < item_value:
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


    def buy_goal(self, loc, decision_type=None):
        """
        Author: Calum McConville
        Function takes a market that has been researched and returns the 
        recommended buying action (if any) based on goals
        
        @param loc is the location of the market that has been researched
        @param goals is the goals we want to consider
        @return (item, qty) the name of an item and quantity to purchase (or None)
        """

        purchase_amt = None
        goal_assessment = []
        
        for item in self.needs:
            if item in self.market_history[loc] and self.needs[item] > 0:
                value = (self.market_history[loc][item][0] * self.goal[item])/10000

                #only want goal items that will provide 20% return at end of game
                if value <= 0.8:
                    goal_assessment.append((value, item))
                
                #if we are in a position to reach our goal, prioritise this
                elif self.market_history[loc][item][0] >= self.needs[item] and \
                value < 1:
                    goal_assessment.append((0, item))
        
        if goal_assessment and decision_type == "investigate":
            return "research"

        #we've found a goal item at a price that will give use 20% return
        elif goal_assessment:
            #purchase the highest value goal item
            best_goal = sorted(goal_assessment)[0][1]
            
            #Buy either the store quantity, affordable quantity or goal quantity
            purchase_amt = min(
                int(self.budget_amt(best_goal, loc, self.current_balance)),
                self.market_history[loc][best_goal][1],
                self.needs[best_goal]
                )

            #update state to reflect purchase
            self.inventory[best_goal] += purchase_amt
            self.current_balance -= purchase_amt * self.market_history[loc][best_goal][0]
            self.needs[best_goal] -= purchase_amt
            #return purchase decision
            return (str(best_goal), int(purchase_amt))


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

    def get_safe_neighbour_market(self, location, bm):
        """
        Author: Jason Wang, Stephanie Zhou
        # check whether the adjacent markets are safe markets
        """

        safe_neighbour_list = []
        for i in self.map.map_data['node_graph']['location']:
            if i not in bm:
                safe_neighbour_list.append(i)
        return safe_neighbour_list

    def get_safe_market_list(self, bm):
        """
        Author: Jason Wang, Stephanie Zhou
        # check safe markets
        # return a list of safe markets
        """

        safe_market_list = []
        for i in self.map.map_data['node_graph']:
            if i not in bm:
                safe_market_list.append(i)
        return safe_market_list

    def path_between_two_nodes(self, n1, n2):

        # tests whether n2 is a valid destination
        if n2 not in self.map.map_data['node_graph']:
            return False

        else:
            # set distance to inf for all nodes and 0 for current node
            distances = {vertex: float("inf") for vertex in self.map.map_data['node_graph'].keys()}
            distances[n1] = 0

            # set all nodes as unvisited
            previous_vertices = {vertex: None for vertex in self.map.map_data['node_graph'].keys()}
            vertices = list(self.map.map_data['node_graph'].keys()).copy()

            while vertices:
                # select unvisited node with smallest distance as current position
                current_node = min(vertices, key=lambda vertex: (distances[vertex], vertex))
                print(f"current node = {current_node}")

                # break if smallest distance among unvisited is infinity (something is wrong)
                if distances[current_node] == float("inf"):
                    break

                """
                checks the cost of moving to each of the nodes neighbouring the current node.
                Nodes that are either black or grey receive an additional penalty
                """
                for neighbour in self.map.map_data['node_graph'][current_node]:
                    print(f"neighbour = {neighbour}")

                    alternative_route = distances[current_node] + 1

                    # check if this is currently the fastest way to reach the neighbour
                    if alternative_route < distances[neighbour]:
                        distances[neighbour] = alternative_route
                        # if we've discovered a new fastest route update the access node
                        previous_vertices[neighbour] = current_node

                # Remove current node from unvisited nodes
                vertices.remove(current_node)

            path, current_node = deque(), n2

            # generate path by moving through linked list to create path
            while previous_vertices[current_node] is not None:
                path.appendleft(current_node)
                current_node = previous_vertices[current_node]
            if path:
                path.appendleft(current_node)
                return list(path)


    def safe_path(self, location, bm):
        """
        Author: Stephanie Zhou, Jason Wang, Himansh Mishra

        # return the next market to go
        """

           safe_step = ''
           safe_list = self.get_safe_market_list(self, location, bm)
           safe_neighbours = self.get_safe_neighbour_market(self, location, bm)

           # if the neighbouring market is safe
           if safe_neighbours != []:
               safe_step = safe_neighbours[random.randint(0, len(safe_neighbours))]

           # if the current market is the only safe market
           elif len(safe_list) == 1 and location == safe_list[0]:
               safe_step = None

           # if no neighbouring market is safe, the next step we take go to the closest safe market
           else:
               node_steps = {}
               for i in safe_list:
                   safe_step = path_between_two_nodes(location, i)
                   node_steps[i] = len(safe_step)
               min_step = min(node_steps.values())
               safe_nodes = [k for k, v in node_steps if v = min_step]
               safe_step = self.path_between_two_nodes(location,safe_nodes[random.randint(0,len(safe_nodes))])[0]

           return safe_step



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
        #print(f"current location is {location}")
        #print(f"Path = {self.destination}")
        #print(f"Inventory = {self.inventory}")
        #print(f"black markets = {bm}")
        #print(f"current balance = {self.current_balance}")

        assert isinstance(location, str)
        assert isinstance(prices, dict)
        assert isinstance(info, dict)
        
        #keep track of the stage of the game and available gold balance
        self.turn += 1

        if self.turn == 1:
            self.needs = self.goal.copy()
            #create buffer amount to prevent accruing debt
            self.current_balance = self.gold - self.savings 

        if location in bm:
            self.current_balance -= 100

        if self.current_balance < 0:
            self.current_balance -= self.current_balance * 0.10
        
        #Update market_history based on new information or prices received that turn
        if info:
            
            #Add information to market_history
            for market in info:
                #as long as we don't already have the market information
                if market not in self.market_history:
                    self.market_history[market] = \
                    {k: (v, None) for (k, v) in info[market].items()}

        if prices:
            #Uses prices to update or add information stored in market_history
            self.market_history[location] = prices


        if len(self.market_history) < 8:
            #We have minimal information and should only really make an assessment on goals

            if prices:
                #we have researched the market and want to decide whether to buy or sell
                #makes decision whether to buy at market and returns decision
                instruction = self.buy_goal(location)
                if instruction:
                    return (Command.BUY, instruction)
                else:
                    #move randomly based away from grey and black region
                    #INSERT FUNCTION HERE
                    options = [x for x in list(self.map.get_neighbours(location)) \
                    if x not in bm + gm]
                    
                    return (Command.MOVE_TO, options[random.randint(0, len(options) - 1)])


            elif self.market_history:
                #Market is not researched but we have current information
                
                #calculates average prices based on current market information
                if location in self.market_history:
                    if self.buy_goal(location, decision_type="investigate") == "research":
                        return (Command.RESEARCH, None)
                    else:
                        #move randomly based away from grey and black region
                        #INSERT FUNCTION HERE
                        options = [x for x in list(self.map.get_neighbours(location)) \
                        if x not in bm + gm]
                        
                        return (Command.MOVE_TO, options[random.randint(0, len(options) - 1)])

                else:
                    #we have no information about the current market
                    return (Command.RESEARCH, None)
            
            else:
                #We have no information about any markets
                return (Command.RESEARCH, None)

        #Start optimising location
        elif len(self.market_history) >= 8:

            if not self.destination:
               
                if self.current_balance > 2000 and self.turn < 290:
                    turn_value = 400 + self.turn
                    turn_max = self.optimise_decision(self.market_item_buy_value, \
                        location, bm, gm)

                    #MAKE INTO A FUNCTION
                    #We don't have information about our current market
                    #solution = converge_solution(turn_max)
                    if 0 not in turn_max:
                        #we haven't researched current location
                        current_solution = (0, location)

                    else:
                        current_solution = turn_max[0]

                    for n_turn in turn_max:
                        if turn_max[n_turn][0] > current_solution[0] - (n_turn * turn_value):
                            current_solution = turn_max[n_turn]

                    if current_solution[1] == location:
                        if prices:
                            self.destination = []
                            decision = self.market_item_buy_value(location, decision_type="buy")
                            if isinstance(decision, int):
                                return (Command.PASS, None)

                            return (Command.BUY, decision)
                        
                        else:
                            self.destination = ["buy"]                            
                            return (Command.RESEARCH, None)
                    else:
                        self.destination = list(self.dijkstra_lite(location, current_solution[1], \
                         bm, gm))[1:] + ['sell']
                        next_step = self.destination.pop(0)
                        return (Command.MOVE_TO, next_step)

                else:
                    turn_value = 200 + self.turn
                    #SELLING
                    #Assign a value on each turn with turns being more valuable later in game
                    turn_max = self.optimise_decision(self.value_inventory, \
                        location, bm, gm)
                    
                    #We don't have information about our current market
                    #FUNCTION START
                    if 0 not in turn_max:
                        #we haven't researched current location
                        current_solution = (0, location)

                    else:
                        current_solution = turn_max[0]

                    for n_turn in turn_max:
                        if turn_max[n_turn][0] > current_solution[0] - (n_turn * turn_value):
                            current_solution = turn_max[n_turn]

                    #FUNCTION STOP
                    if current_solution[1] == location:
                        if prices:
                            decision = self.value_inventory(location, decision_type="sell")
                            
                            #CAN PROBABLY DELETE IN FINAL PROGRAM
                            if isinstance(decision, int):
                                
                                return (Command.PASS, None)

                            return (Command.SELL, decision)
                        
                        else:
                            self.destination = ["sell"]                            
                            return (Command.RESEARCH, None)
                    else:
                        self.destination = list(self.dijkstra_lite(location, current_solution[1] \
                            , bm, gm))[1:] + ['sell']
                        next_step = self.destination.pop(0)
                        
                        return (Command.MOVE_TO, next_step)

            else:
                if self.destination == ['sell']:
                    if prices:
                        self.destination = []
                        decision = self.value_inventory(location, decision_type="sell")
                        
                        #CAN PROBABLY DELETE IN FINAL PROGRAM
                        if isinstance(decision, int):
                            return (Command.PASS, None)
                        
                        return (Command.SELL, decision)
                    
                    else:
                        return (Command.RESEARCH, None)

                elif self.destination == ["buy"]:
                    
                    if prices:
                        self.destination = []
                        decision = self.market_item_buy_value(location, decision_type="buy") 
                        
                        if isinstance(decision, int):
                            return (Command.PASS, None)

                        return (Command.BUY, decision)
                    
                    else:
                        return (Command.RESEARCH, None)

                else:
                    next_step = self.destination.pop(0)
                    return (Command.MOVE_TO, next_step)
