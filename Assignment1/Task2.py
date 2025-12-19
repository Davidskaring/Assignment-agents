import random
from mesa import Model
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid


# ---------------------------------------------------------
# 1. AGENTEN
# ---------------------------------------------------------
class WorkerAgent(CellAgent):
    def __init__(self, model, cell, capacity=2):
        super().__init__(model)
        self.cell = cell
        self.capacity = capacity
        self.my_jobs = []  # Lista för att hålla tasks

    def is_worker_available(self):

        if len(self.my_jobs) < self.capacity:
            return True
        else:
            return False

class ParkAgent(CellAgent):
    """An agent with fixed initial wealth."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        # SET WEALTH ÄNDRAR FÄRGEN BARA ATM
        self.wealth = 0


# ---------------------------------------------------------
# 2. TASK
# ---------------------------------------------------------
class Task:
    def __init__(self, id, duration, resources):
        self.id = id
        self.duration = duration
        self.resources = resources  # Hur många agenter krävs?

# 3. MODELLEN


class SchedulerModel(Model):
    def __init__(self, num_agents=3, num_tasks=50):
        super().__init__()
        WorkerAgent.create_agents(
            self.so,
            num_agents,
            capacity=2  # Skickas till agentens __init__
        )
        self.grid = OrthogonalMooreGrid((5, 10), random=self.random)
        self.datacollector = DataCollector(
            # denna kommer från funktionen nedanför som räknar antal bilar som är parkerade
            model_reporters={"Occupied Spots": self.count_occupied_spots},
            # wealth får fungera som en av ovh på knapp för påsatta bilar
            agent_reporters={"Wealth": "wealth"}
        )



    def step(self):
        # Här kommer logiken för att tilldela tasks till agenter senare
        pass





