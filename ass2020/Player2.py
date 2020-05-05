from BasePlayer import BasePlayer
import Command
from collections import deque, defaultdict
import random
from statistics import mean


class Player(BasePlayer):


    def __init__(self):
        #Instance variables that keep track of information throughout the game

        self.market_history = {} #combination of market research and info
        self.turn = 0
        self.inventory = defaultdict(int) #current player items and quantity in possession
        self.instructions = []
        self.needs = None #will store achievable goal
        self.savings = 1000
        self.current_balance = 0
        

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
        for market in self.market_history.keys():
            for item in self.market_history[market].keys():
                averages[item].append(self.market_history[market][item][0])
        
        #creates averages of each item based on current information
        averages = {k: mean(v) for k, v in averages.items()}
        return averages

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

    
    def buy_choice(self, loc):
        """
        Author: Calum McConville
        Function takes a market that has been researched and returns the 
        recommended buying action (if any) based on goals and stock items
        
        @param loc is the location of the market that has been researched
        @return (item, qty) the name of an item and quantity to purchase (or None)
        """

        #return current average prices based on known information
        avg_prices = self.average_prices()
        purchase_amt = None
        goal_assessment = []
        
        for item in self.needs:
            if item in self.market_history[loc] and self.needs[item] > 0:
                value = (self.market_history[loc][item][0] * self.goal[item])>10000

                #only want goal items that will provide 20% return at end of game
                if value < 0.8:
                    goal_assessment.append((value, item))
                
                #if we are in a position to reach our goal, prioritise this
                elif self.market_history[loc][item][0] >= self.needs[item] and \
                value < 1:
                    goal_assessment.append((0, items))
                    

        #we've found a goal item at a price that will give use 20% return
        if goal_assessment:
            #purchase the highest value goal item
            best_goal = sorted(goal_assessment)[0][1]
            
            #Buy either the store quantity, affordable quantity or goal quantity
            purchase_amt = min(
                int(self.budget_amt(best_goal, loc, self.gold - self.savings)),
                self.market_history[loc][best_goal][1],
                self.needs[best_goal]
                )

            #update state to reflect purchase
            self.inventory[best_goal] = purchase_amt
            self.current_balance -= purchase_amt * self.market_history[loc][best_goal][0]
            self.needs[best_goal] -= purchase_amt
            #return purchase decision
            return (str(best_goal), purchase_amt)



            

        """
        for item in self.market_history[loc].keys():

            if item in self.needs and self.needs[item] > 0:
                
                #How much value does this price represent relative to our goal
                value = (self.market_history[loc][item][0] * self.goal[item])/10000


                if self.market_history[loc][item][1] >= self.needs[item] \
                    and self.market_history[loc][item][0] * self.needs[item] < 10000:

                    
                    purchase_amt = int(self.budget_amt(item, loc, self.gold - self.savings))
                    
                    self.needs[item] -= purchase_amt
                    print(f"Command = {(Command.BUY, (str(item), purchase_amt))}")
                    return (str(item), purchase_amt)

                elif self.market_history[loc][item][0] <= avg_prices[item]:
                    print(f"goal item below avg= {item}")
                    #NEED TO ADJUST BUDGET
                    purchase_amt = int((self.budget_amt(item, loc, 5000), self.needs[item]//2))
                    self.needs[item] -= purchase_amt
                    print(f"Command = {(str(item), purchase_amt)}")

                    return (str(item), purchase_amt)
        """

    def get_safe_neighbour_market(self, location, bm):
        # check whether the adjacent markets are safe markets
        safe_neighbour_list = []
        for i in self.map.map_data['node_graph']['location']:
            if i not in bm:
                safe_neighbour_list.append(i)
        return safe_neighbour_list

    def get_safe_market_list(self, bm):
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

     # return the next market to go

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

        @returns (cmd, data) cmd is one of Command.* and data is a tuple of necessary data for a command or None.
        """
        
        #return (Command.PASS, None)
        assert(type(location) is str)
        assert(type(prices) is dict)
        assert(type(info) is dict)
        
        #keep track of the stage of the game
        self.turn += 1

        if self.turn == 1:
            self.needs = self.goal.copy()
            self.current_balance = self.gold
        
        #Always add any new information from other players to market_history in same format as prices
        if info:
            
            #Add information to market_history
            for market in info.keys():
                #as long as we don't already have the market information
                if market not in self.market_history:
                    self.market_history[market] = \
                    {k: (v, None) for (k, v) in info[market].items()}


        if prices:
            #we have researched the market and want to decide whether to buy or sell


            #Uses prices to update or add information stored in market_history
            self.market_history[location] = prices

            #makes decision whether to buy at market and returns decision
            instruction = self.buy_choice(location)

            if instruction:
                return (Command.BUY, instruction)

            else:
                #move
                options = list(self.map.get_neighbours(location))
                return (Command.MOVE_TO, options[random.randint(0, len(options) - 1)])


        elif self.market_history:
            #Market is not researched but we have current information
            
            #calculates average prices based on current market information
            if location in self.market_history:
                avg_prices = self.average_prices()
                for item in self.market_history[location].keys():
                    if item in avg_prices and \
                     self.market_history[location][item][0] < avg_prices[item]:
                        return (Command.RESEARCH, None)
# why research, not buy?

                else:
                    #move on if there are no reasonably priced items
                    options = list(self.map.get_neighbours(location))
                    return (Command.MOVE_TO, options[random.randint(0, len(options) - 1)])


            else:
                #we have no information about the current market
                return (Command.RESEARCH, None)
                
                #if location in bm:
                    #probably try and get out
                #    path = get_out(self, location) #tells us shortest path out of black and grey

                #else:
                #    return (Command.RESEARCH, None)
        
        else:
            #WE HAVE NO INFORMATION ABOUT ANY MARKETS IN THE GAME
            return (Command.RESEARCH, None)

    


 

#self.map.get_neighbours(node_name)

#self.map.is_road(n1, n2)


