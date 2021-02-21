DEBUG = False


def log(message: str):
    if DEBUG:
        print(message)


def filter_prg(stm, rule_set):
    if "base" not in str(stm):
        rule_set.append(stm)
