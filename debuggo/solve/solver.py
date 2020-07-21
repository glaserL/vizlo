
class Solver():
    
    def __init__(self, stable_models):
        self.stable_models = stable_models

    def get_branch(self, head, stable_models):
        trues, falses = [], []
        for stable_model in stable_models:
            if head in stable_model:
                trues.append(stable_model)
            else:
                falses.append(stable_model)
        return trues, falses


    def next_try(self, prev_stack_until_now, definition_history, i):
        trues, falses = self.get_branch(definition_history[i], self.stable_models)
        # abbruch bedingung
        if i == len(definition_history) - 1:
            final_paths = []
            if len(trues):
                new_path = prev_stack_until_now + [definition_history[i]]
                final_paths.append(new_path)
            if len(falses):
                new_path = prev_stack_until_now + [f"not_{definition_history[i]}"]
                final_paths.append(new_path)
            return final_paths
        else:
            paths = []
            if len(trues):
                new_path = prev_stack_until_now + [definition_history[i]]
                paths.extend(self.next_try(new_path, definition_history, i+1))
            if len(falses):
                new_path = prev_stack_until_now + [f"not_{definition_history[i]}"]
                paths.extend(self.next_try(new_path, definition_history, i+1))
            return paths

    def generate_path(self, definition_history):
        paths = self.next_try([], definition_history, 0)
        return paths