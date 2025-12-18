#Has multi-dimensional arrays and matrices.
# Has a large collection of mathematical functions to operate on these arrays.
from itertools import count

import numpy as np

# Data manipulation and analysis.
import pandas as pd

# Data visualization tools.
import seaborn as sns

import mesa
from mesa import space, DataCollector
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from mesa.examples import BoltzmannWealth
from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle, make_space_component
from mesa.space import MultiGrid



import mesa
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from mesa.visualization import SolaraViz, make_plot_component, make_space_component


# -------------------------------------------------------------------------
# 1. AGENT CLASS
# -------------------------------------------------------------------------

class CarAgent(CellAgent):
    """An agent with fixed initial wealth."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        self.paused = False
        self.wealth = 1

    def move(self):
        self.cell = self.cell.neighborhood.select_random_cell()

    def pause(self):
        self.paused = True

    def park(self):
        cellmates = [a for a in self.cell.agents if a is not self]
        if cellmates:
            self.pause()
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def step(self):
        count = 0
        self.move()
        if self.move():
            count +=1



class ParkAgent(CellAgent):
    """An agent with fixed initial wealth."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        self.wealth = 1

    def move(self):
        self.cell = self.cell.neighborhood.select_random_cell()

    def give_money(self):
        cellmates = [a for a in self.cell.agents if a is not self]
        if cellmates:
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()


# --
# -------------------------------------------------------------------------
# 2. MODEL CLASS
# -------------------------------------------------------------------------

class BoltzmannWealth(Model):
    """A simple model of an economy where agents exchange currency at random."""

    def __init__(self, n=100, width=10, height=10, seed=None, p=5):
        super().__init__(seed=seed)
        self.num_agents = n
        self.grid = OrthogonalMooreGrid((width, height), random=self.random)

        self.datacollector = DataCollector(
            model_reporters={"Gini": self.compute_gini},
            agent_reporters={"Wealth": "wealth"},
        )

        # Skapa agenter
        CarAgent.create_agents(
            self,
            self.num_agents,
            self.random.choices(self.grid.all_cells.cells, k=self.num_agents),
        )

        ParkAgent.create_agents(
            self,
            self.num_agents,
            self.random.choices(self.grid.all_cells.cells, k=self.num_agents),
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)

    def compute_gini(self):
        agent_wealths = [agent.wealth for agent in self.agents]
        x = sorted(agent_wealths)
        n = self.num_agents
        if n == 0 or sum(x) == 0: return 0
        b = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x))
        return 1 + (1 / n) - 2 * b


# -------------------------------------------------------------------------
# 3. VISUALIZATION (SOLARA) - KORRIGERAD
# -------------------------------------------------------------------------

def agent_portrayal(agent):
    # Enklare sätt att bestämma färg och storlek
    return {
        "color": "tab:purple" if agent.wealth > 0 else "tab:grey",
        "size": 50,
        "alpha": 0.8
    }


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "n": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of Car Agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },"p": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of Parking Agents",
        "min": 3,
        "max": 5,
        "step": 1,
    },

    "width": 10,
    "height": 10,
}

# 1. Skapa modellen
model = BoltzmannWealth(50, 10, 10)

# 2. Skapa graf-komponenter på det "säkra" sättet
SpaceGraph = make_space_component(agent_portrayal)
GiniPlot = make_plot_component("Gini")

# 3. Starta SolaraViz
page = SolaraViz(
    model,
    components=[SpaceGraph, GiniPlot],  # Lägg in både kartan och grafen här
    model_params=model_params,
    name="Parking Space Agent Program",
)