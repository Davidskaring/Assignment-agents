import random
from mesa import Model, DataCollector
from mesa.agent import AgentSet
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from numpy.ma.core import append


# ---------------------------------------------------------
# 1. AGENTEN
# ---------------------------------------------------------
class WorkerAgent1(CellAgent):
    def __init__(self, model, cell, capacity=2):
        super().__init__(model)
        self.cell = cell
        self.capacity = capacity
        self.my_jobs = []  # Lista för att hålla tasks
        self.busy = False
        self.stepcd = 0

    def working(self):

        for a in self.cell.agents:
            if isinstance(a, TaskAgent) and not self.busy:
                self.stepcd += self.duration


    def is_worker_available(self):

        if len(self.my_jobs) < self.capacity:
            return True
        else:
            return False


class WorkerAgent2(CellAgent):
    def __init__(self, model, cell, capacity=1):
        super().__init__(model)
        self.cell = cell
        self.capacity = capacity
        self.my_jobs = []  # Lista för att hålla tasks


class WorkerAgent3(CellAgent):
    def __init__(self, model, cell, capacity=2):
        super().__init__(model)
        self.cell = cell
        self.capacity = capacity
        self.my_jobs = []  # Lista för att hålla tasks



class TaskAgent(CellAgent):
    """An agent with fixed initial wealth."""

    def __init__(self, model, cell, id, duration, resources, task, tasklist):
        super().__init__(model)
        self.cell = cell
        self.id = id
        self.duration = random.randint(10,20)
        self.resources = random.randint(1, 3)
        self.task = 50
        self.tasklist = []

    def taskcreate(self):

        for n in range (self.task):
            tasks = self.duration , self.resources , self.id
            self.tasklist.append(tasks)




# 3. MODELLEN


class SchedulerModel(Model):
    def __init__(self, t=1, num_tasks=50):
        super().__init__()
        self.num_WrokerAgent1 = t
        self.num_WrokerAgent2 = t
        self.num_WrokerAgent3 = t
        self.num_TaskAgents = num_tasks



        WorkerAgent1.create_agents(
            self,
            self.num_WrokerAgent1,
      # Skickas till agentens __init__
        )

        WorkerAgent2.create_agents(
            self,
            self.num_WrokerAgent2,
            # Skickas till agentens __init__
        )

        WorkerAgent3.create_agents(
            self,
            self.num_WrokerAgent3,
            # Skickas till agentens __init__
        )

        TaskAgent.create_agents(
            self.sort(self),
            self.num_TaskAgents,

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