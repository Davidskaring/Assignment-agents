
from mesa.visualization.components import AgentPortrayalStyle, make_space_component
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from mesa.visualization import SolaraViz, make_plot_component, make_space_component
import random

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
        self.busy = False
        self.stepcd = 0


    def move(self):
        self.cell = self.cell.neighborhood.select_random_cell()

    def pause(self):
        self.paused = True

    def park(self):
        for a in self.cell.agents:
            if isinstance(a,ParkAgent) and not self.busy:
                self.paused = True
                self.busy = True
                self.stepcd += random.randint(3, 5)
                return

    def unpark(self):
        self.paused = False

    def step(self):
        if self.paused:
            self.stepcd -= 1
            if self.stepcd == 0:
                self.unpark()
                self.busy = False
            return
        self.move()
        self.park()


class ParkAgent(CellAgent):
    """An agent with fixed initial wealth."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        # SET WEALTH ÄNDRAR FÄRGEN BARA ATM
        self.wealth = 0

# -------------------------------------------------------------------------
# 2. MODEL CLASS
# -------------------------------------------------------------------------

class ParkingModel(Model):
    """A simple model of an economy where agents exchange currency at random."""

    def __init__(self, n=100, width=10, height=10, seed=None, p=5):
        super().__init__(seed=seed)
        self.num_ParkAgent = p
        self.num_CarAgent = n

        self.grid = OrthogonalMooreGrid((width, height), random=self.random)

        self.datacollector = DataCollector(
            # denna kommer från funktionen nedanför som räknar antal bilar som är parkerade
            model_reporters={"Occupied Spots": self.count_occupied_spots},
            # wealth får fungera som en av ovh på knapp för påsatta bilar
            agent_reporters={"Wealth": "wealth"}
        )

        # Skapa agenter
        CarAgent.create_agents(
            self,
            self.num_CarAgent,
            self.random.choices(self.grid.all_cells.cells, k=self.num_CarAgent),
        )

        ParkAgent.create_agents(
            self,
            self.num_ParkAgent,
            self.random.choices(self.grid.all_cells.cells, k=self.num_ParkAgent),
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)


    #nya funktionen för att räkna varje bilagent när den står parkerad i 3-5 steps
    def count_occupied_spots(self):
        count = 0
        # loopa igenom alla agenter
        for agent in self.agents:
            # Om det är en bil och den är pausad då har den ju en plats
            if isinstance(agent, CarAgent) and agent.paused:
                count += 1
        return count


# -------------------------------------------------------------------------
# 3. VISUALIZATION (SOLARA)
# -------------------------------------------------------------------------

def agent_portrayal(agent):
    portrayal = AgentPortrayalStyle(size=50, color="tab:orange")
    if agent.wealth > 0:
        portrayal.update(("color", "tab:blue"), ("size", 100))
    return portrayal

    # Enklare sätt att bestämma färg och storlek


#    return {
#        "color": "tab:purple" if agent.wealth > 0 else "tab:grey",
#        "size": 50,
#        "alpha": 0.8
#   }


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
        "min": 1,
        "max": 10,
        "step": 1,
    }, "p": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of Parking Agents",
        "min": 1,
        "max": 10,
        "step": 1,
    },

    "width": 10,
    "height": 10,
}

# 1. Skapa modellen
model = ParkingModel(50, 10, 10)

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