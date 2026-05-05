class Iteration:
    def __init__(self, thought, action, result=None):
        self.thought = thought
        self.action = action
        self.result = result
        self.labels = []

    def add_label(self, label):
        if label not in self.labels:
            self.labels.append(label)

    def to_dict(self):
        return {"thought": self.thought, "action": self.action, "result": self.result}

    def __str__(self):
        return f"Iteration(thought={self.thought!r}, action={self.action!r}, result={self.result!r}, labels={self.labels})"


class Task:
    def __init__(self, context, goals, tools, end_criteria):
        self.context = context
        self.goals = goals
        self.tools = tools
        self.end_criteria = end_criteria


class Trajectory:
    def __init__(self, name, iterations, task=None):
        self.name = name
        self.iterations = list(iterations)
        self.task = task

    @classmethod
    def from_dicts(cls, name, iteration_dicts, task=None):
        iters = [
            Iteration(d.get("thought", ""), d.get("action", ""), d.get("result"))
            for d in iteration_dicts
        ]
        return cls(name, iters, task=task)

    def add_iteration(self, iteration):
        self.iterations.append(iteration)

    def get_metrics(self):
        return {
            "total_actions": len(self.iterations),
            "action_redundancy": self.calculate_action_redundancy(),
        }

    def calculate_action_redundancy(self):
        counts = {}
        for it in self.iterations:
            key = str(it.action)
            counts[key] = counts.get(key, 0) + 1
        return sum(c - 1 for c in counts.values() if c > 1)

    def __str__(self):
        return f"Trajectory(name={self.name}, iterations={len(self.iterations)})"
