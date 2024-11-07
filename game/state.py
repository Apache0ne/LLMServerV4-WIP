class GameState:
    def __init__(self, context_name, initial_state):
        self.context_name = context_name
        self.current_state = initial_state
        self.history = [initial_state]

    def update(self, new_state):
        self.current_state = new_state
        self.history.append(new_state)

    def get_current_state(self):
        return self.current_state

    def get_history(self):
        return self.history

    def rollback(self, steps=1):
        if len(self.history) > steps:
            self.history = self.history[:-steps]
            self.current_state = self.history[-1]
        else:
            raise ValueError("Cannot rollback that many steps")