#Has multi-dimensional arrays and matrices.
# Has a large collection of mathematical functions to operate on these arrays.
from itertools import count

import numpy as np
import random
# Data manipulation and analysis.
import pandas as pd

# Data visualization tools.
import seaborn as sns


from mesa.visualization.components import AgentPortrayalStyle, make_space_component
from mesa.space import MultiGrid



import mesa
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from mesa.visualization import SolaraViz, make_plot_component, make_space_component



# 1. Agent Class Creation
# -------------------------------------------------------------------------

class CarAgent(CellAgent):
    """An agent meant to simulate a car looking for parkingspots."""

# constructor for our car agent
    # we initiate car agent so it inherits from mesas cell agent
    # we have 5 attributes for this agent where cell is mesa related attribute
    # and the rest are our created attributes from us
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        self.paused = False
        self.wealth = 1
        self.busy = False
        self.stepcd = 0

# here we define our move function
    def move(self):
        #our agent will move by random to a new cell
        self.cell = self.cell.neighborhood.select_random_cell()

    # here we define our pause function which should simulate parking
    def pause(self):
        #the function set the value to true and then the caragent will stop moving
        self.paused = True

# here we define our park method
    def park(self):
        # we use a forloop to look for other agents in the same cell
        for a in self.cell.agents:
            #if we find a agent and it is a park agent and lastly if its not busy.
            #busy means if the cell has antoher car agent parked in the cell
            #the car agent will park and we add a int between 3 and 5 to stepcd(cooldown)
            if isinstance(a,ParkAgent) and not self.busy:
                self.paused = True
                self.busy = True
                self.stepcd += random.randint(3, 5)
                return
#here we define our unpark function
    def unpark(self):
        #set the value to false so the parkagent will begin to move again
        self.paused = False

# here we define our unpark function
    def step(self):
        #we use a if statement for all the parked caragents
        #so every step lower the step cooldown by 1 int
        # and when the cooldown reach 0 in value the
        #car agen will unpark and stop being busy
        if self.paused:
            self.stepcd -=1
            if self.stepcd == 0:
                self.unpark()
                self.busy = False
            return
        #we also include this to method in every step
        self.move()
        self.park()



# this is the constructor for our  Parkagent
    # we initiate  Parkagent so it inherits from mesas cell agent
    # we have the attribute wealth in this agent which at the moment only
    # changes color of the agent in the visualization.
class ParkAgent(CellAgent):
    """An agent with fixed spot in the grid."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        self.wealth = 0




# 2. ParkingModel CLASS
# -------------------------------------------------------------------------

class ParkingModel(Model):
    """A simple model of Parking."""

# constructour for our parking model
    # we initiate the model with number of Caragents, width and height of the grid
    # and seed if we wanna reproduce a test
    #and lastly number of Parkagents
    def __init__(self, n=15, width=10, height=10, seed=None, p=15):
        super().__init__(seed=seed)
        self.num_CarAgent = n
        self.num_ParkAgent = p


        #here we create our 2d-grid useing the mooore grid from mesa
        self.grid = OrthogonalMooreGrid((width, height), random=self.random)

        #we use data collecter to collect model and agent statistics
        self.datacollector = DataCollector(
            # this model reporter counts how many parking spots are occupied at the moment
            model_reporters={"Occupied Spots": self.count_occupied_spots}
        )

        # here we create Caragent instances and place them randomly on the grid.
        CarAgent.create_agents(
            self,
            self.num_CarAgent,
            self.random.choices(self.grid.all_cells.cells, k=self.num_CarAgent),
        )
        # here we create Parkagent instances and place them randomly on the grid.
        ParkAgent.create_agents(
            self,
            self.num_ParkAgent,
            self.random.choices(self.grid.all_cells.cells, k=self.num_ParkAgent),
        )


    def step(self):
        #here is were we exectue the step in the "simulation
        #we use shuffle_do so all the agents perform the step method in a random order
        #this is to prevent ordering favor
        self.agents.shuffle_do("step")
        #datacollector so we collect data after each step
        self.datacollector.collect(self)


    #nya funktionen för att räkna varje bilagent när den står parkerad i 3-5 steps
    #here we the fucntion for counting the number of Caragents currently parked
    def count_occupied_spots(self):
        count = 0
        #we loop thorugh all the agents
        for agent in self.agents:
            # if there is a agent, CarAgent and it is paused we add one the the count
            if isinstance(agent, CarAgent) and agent.paused:
                count += 1
        return count


#  VISUALIZATION
# -------------------------------------------------------------------------

def agent_portrayal(agent):
    portrayal = AgentPortrayalStyle(size=50, color="tab:orange")
    if agent.wealth > 0:
        portrayal.update(("color", "tab:blue"), ("size", 100))
    return portrayal



model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "n": {
        "type": "SliderInt",
        "value": 15,
        "label": "Number of Car Agents:",
        "min": 1,
        "max": 15,
        "step": 1,
    }, "p": {
        "type": "SliderInt",
        "value": 15,
        "label": "Number of Parking Agents",
        "min": 1,
        "max": 15,
        "step": 1,
    },

    "width": 10,
    "height": 10,
}

# 1. Skapa modellen
model = ParkingModel()

# 2. Skapa graf-komponenter på det "säkra" sättet
SpaceGraph = make_space_component(agent_portrayal)
#Denna ändrade jag från Gini skiten till en statsplot istället från occupied slots
StatsPlot = make_plot_component("Occupied Spots")

# 3. Starta SolaraViz
page = SolaraViz(
    model,
    #Här skickar vi in statsplot till solarawiz
    components=[SpaceGraph, StatsPlot],  # Lägg in både kartan och grafen här
    model_params=model_params,
    name="Parking Space Agent Program",
)