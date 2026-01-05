from mesa.visualization.components import AgentPortrayalStyle, make_space_component, make_plot_component
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from mesa.visualization import SolaraViz
import random


# -------------------------------------------------------------------------
# 1. TASK CLASS
# -------------------------------------------------------------------------
class Task:
    """
    Simple Task class representing a task
    It holds the ID, how long it takes (duration) and how many agents are needed.
    """

    def __init__(self, id, duration, resources):
        self.id = id
        self.duration = duration
        self.resources = resources


# -------------------------------------------------------------------------
# 2. AGENT CLASS
# -------------------------------------------------------------------------
class Workeragent(CellAgent):
    """
    Represents a worker agent that can handle multiple tasks
    """

    def __init__(self, model, cell, capacity):
        super().__init__(model)
        self.cell = cell
        self.capacity = capacity  # Max number of concurrent tasks (1 or 2)
        self.jobs = []  # List of tasks currently being worked on


# -------------------------------------------------------------------------
# 3. TaskModel that handles the scheduling of tasks
# -------------------------------------------------------------------------
class TaskModel(Model):
    """
    The main simulation model that handles task generation and scheduling.
    """

    def __init__(self, num_agents=3, num_tasks=50, width=5, height=5, seed=None):
        super().__init__(seed=seed)
        self.steps = 0

        # Here we initialize the grid
        self.grid = OrthogonalMooreGrid((width, height), random=self.random)

        #Here the agents are created in a list
        self.agents_list = []
        for i in range(num_agents):
            #Place agents in a simple row on the grid (i is for column)
            cell = self.grid[(2, i)]

            # Randomize capacity to be either 1 or 2
            cap = random.randint(1, 2)

            #Create and add the agent
            a = Workeragent(self, cell, capacity=cap)
            cell.add_agent(a)
            self.agents_list.append(a)
            self.agents.add(a)

        # Here we create the tasks
        #Generate a queue of tasks with varying duration and resource requirements
        self.queue = []
        for i in range(num_tasks):
            # Duration= 5-15 steps, Resources needed = 1-3 agents
            self.queue.append(Task(i, random.randint(5, 15), random.randint(1, 3)))

        self.active_tasks = []  # List to track tasks currently in progress

        # Datacollector
        self.datacollector = DataCollector(
            # here we use model_reporters and use the function get_queue_length to be able to display queue length in solara
            model_reporters={"Tasks in Queue": self.get_queue_length}
        )
        self.datacollector.collect(self)

    #method to collect the queue length needed in datacollector
    def get_queue_length(self):
        return len(self.queue)

    def step(self):
        """
        Here we create logic to move the model forward by one step.
        It handles task progress, completion and assigning new tasks.
        """
        self.steps += 1

        # Print the current step
        print(f'{{"type":"get_step","step":{self.steps}}}')

        # Here is the work phase were all tasks are handled
        # We iterate over a copy of the list [:] to safely remove items while looping
        for task in self.active_tasks[:]:
            task.duration -= 1  # Decrease remaining duration

            # Find all agents working on this specific task
            workers = [a for a in self.agents_list if task in a.jobs]

            # Print status for each agent working on the task
            for agent in workers:
                print(f"Agent {agent.unique_id} is working on Task {task.id}, Task Duration: {task.duration}")

            # Check if task is finished
            if task.duration <= 0:
                self.active_tasks.remove(task)
                # Free up the agents by removing the task from their job list
                for agent in workers:
                    agent.jobs.remove(task)

        # Here is the task scedulinging logic were we assign new tasks to the free agent
        if self.queue:
            next_task = self.queue[0]

            # Identify available agents
            freeAgents = [a for a in self.agents_list if len(a.jobs) < a.capacity]

            # Check if we have enough available agents for the next task
            if len(freeAgents) >= next_task.resources:
                task = self.queue.pop(0)  # Remove from queue
                self.active_tasks.append(task)  # Add to active list

                # Assign the task to the first X available agents
                for i in range(task.resources):
                    freeAgents[i].jobs.append(task)

        # Here is the stop function
        # Stop the simulation automatically when all work is done
        if len(self.queue) == 0 and len(self.active_tasks) == 0:
            self.running = False
            print("All tasks completet")

        self.datacollector.collect(self)


# -------------------------------------------------------------------------
# 4. VISUALIZATION
# -------------------------------------------------------------------------
def agent_portrayal(agent):
    """
    Visualizes cooperation by assigning colors based on Task ID.
    """
    #If the agent is idle (waiting) set the color grey
    portrayal = AgentPortrayalStyle(size=80, color="lightgrey")

    # If the agent is working then:
    if len(agent.jobs) > 0:
        current_task = agent.jobs[0]

        # Check how many agents the task requires
        if current_task.resources > 1:
            # if the task requires more than 1 agent, turn it red
            color = "red"
        else:
            # if the task requires one agent, turn it blue
            color = "blue"

        portrayal.update(("color", color))

    return portrayal


# Solara Parameters
model_params = {
    "num_tasks": {"type": "SliderInt", "value": 50, "label": "Tasks", "min": 10, "max": 100, "step": 10},
    "num_agents": {"type": "SliderInt", "value": 3, "label": "Agents", "min": 1, "max": 5, "step": 1},
}

# Initialize Model and Visualization Components
model = TaskModel()
SpaceGraph = make_space_component(agent_portrayal)
StatsPlot = make_plot_component("Tasks in Queue")

# Launch the Solara App
page = SolaraViz(
    model,
    components=[SpaceGraph, StatsPlot],
    model_params=model_params,
    name="Task 2: Cooperative Agents"
)