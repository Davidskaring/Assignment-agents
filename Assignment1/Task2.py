import random

from mesa.discrete_space import CellAgent

"""
1.
Create 50 tasks with varying duration and resources.
Example
Task 1: Duration = 10 units, Resources = 2 (requires 2 agents to work together).
Task 2: Duration = 15 units, Resources = 3 (requires 3 agents to work together).
Task 3: Duration = 17 units, Resources = 1 (requires 1 agent).
"""
class Task:
    def __init__(self, id, duration, resources):
        self.id = id
        self.duration = duration
        self.resources = resources

    def __repr__(self):
        return f"Uppgift {self.id}: Tid={self.duration}, Kräver={self.resources} pers"

task_list = []

for i in range(50): # [cite: 26]
    # Slumpa tid mellan 5 och 15 sekunder
    tid = random.randint(5, 15)

    # Slumpa resurser: Antingen 1, 2 eller 3 personer behövs
    resurser = random.randint(1, 3)

    # här skapar vi en task
    ny_uppgift = Task(i, tid, resurser)

    # lägger vi lappen i högen
    task_list.append(ny_uppgift)
    # Titta på de 5 första lapparna ---
    print("Här är de 5 första uppgifterna i högen:")
    for task in task_list:
        print(task)

#Här skapar vi agenterna

class WorkerAgent(CellAgent):
    def __init__(self, cell, model, capacity):
        super().__init__(model)
        self.id = id
        self.cell = cell

        #hur många jobb agenten har "kapacitet"
        self.capacity = capacity

        #för att veta hur många jobb agenten har
        self.my_jobs = []

        #funktion för att kolla om agenten är ledig och kan jobba
    def is_worker_available(self):
        if self.my_jobs < self.capacity:
            return True
        else:
            return False