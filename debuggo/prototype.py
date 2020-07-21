import os
import pathlib

def main():
    stable_models = [["d"], ["d", "c"], ["d", "c", "b"], ["d", "c", "b", "a"]]

    definition_history = ["a", "b", "c", "d"] # the sequence of rule heads in the program
    definition_history = list(reversed(definition_history))

    def get_branch(head, stable_models):
        trues, falses = [], []
        for stable_model in stable_models:
            if head in stable_model:
                trues.append(stable_model)
            else:
                falses.append(stable_model)
        return trues, falses


    ROOT = "stack"
    if not os.path.exists(ROOT):
        os.mkdir(ROOT)

    example_paths = "d/not_c/not_b/not_a", "d/c/not_b/not_a"
    # for head in definition_history: # this also gives us "non-recursiveness"
    #     trues, falses = get_branch(head, stable_models)
    #     if len(trues) > 0:



    # i_suck_at_recursiveness([d, not_c], b, [d, c, b, a], 1)
    # def i_suck_at_recursiveness(prev_stack_until_now, current_head_to_add, definition_history, i):
    #     trues, falses = get_branch(current_head_to_add, stable_models)
    #     if len(trues):
    #         future = prev_stack_until_now + current_head_to_add
    #         if len(definition_history) == i-1:
    #             return 
    #         return i_suck_at_recursiveness(future, definition_history[i+1], definition_history, i+1)
    #     if len(falses):
    #         future = prev_stack_until_now + f"not_{current_head_to_add}"
    #         return i_suck_at_recursiveness(future, definition_history[i+1], definition_history, i+1)

    def next_try(prev_stack_until_now, definition_history, i):
        trues, falses = get_branch(definition_history[i], stable_models)
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
                paths.extend(next_try(new_path, definition_history, i+1))
            if len(falses):
                new_path = prev_stack_until_now + [f"not_{definition_history[i]}"]
                paths.extend(next_try(new_path, definition_history, i+1))
            return paths

        # step down o so


    paths = next_try([], definition_history, 0)

    COMMIT = False
    for path in paths:
        mkpath = f"{ROOT}/{'/'.join(path)}"
        print(f"Path: {mkpath}")
        if COMMIT:
            if not os.path.exists(mkpath):
                pathlib.Path(mkpath).mkdir(parents=True)
    return paths
