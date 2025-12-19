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

        if self.my_jobs < self.capacity:
            return True
        else:
            return False


# ---------------------------------------------------------
# 2. TASK
# ---------------------------------------------------------
class Task:
    def __init__(self, id, duration, resources):
        self.id = id
        self.duration = duration
        self.resources = resources  # Hur många agenter krävs?

    def __repr__(self):
        return f"Uppgift {self.id}: Tid={self.duration}, Kräver={self.resources} pers"



# 3. MODELLEN

class SchedulerModel(Model):

    def step(self):
        # Här kommer logiken för att tilldela tasks till agenter senare
        pass





