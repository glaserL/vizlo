

class ASPTransformer():
    """
    Transforms a given ASP program into a reified version.
    """

    def __init__(self):
        raise NotImplementedError

    def transform(self, program):
        print("DEBUGGING MODE")
        return """
h(a,1,(b)) :- b, not a.
h(b,2,(c)) :- c, not b.
h(c,3,(d)) :- d, not c.
h(d,4,()) :- not d.
#external d.
#external c.
#external b.
#external a.
% Original program.
%a :- b.
%b :- c.
%c :- d.
%d.
"""

class IdentityTransformer(ASPTransformer):

    def __init__(self):
        pass

    def transform(self, program):
        return program

class HoldsTransformer(ASPTransformer):
    def __init__(self):
        pass

    def transform(self, program):
        transformed_lines = []
        i = 1
        atoms = set()
        with open("error.log","w") as log:
            for line in program.split("\n"):
                if line.strip().startswith("%"):
                    transformed_lines.append(line)
                elif ":-" in line:
                    split_rule = line.split(":-")
                    head = split_rule[0].strip()
                    literals = split_rule[1].split(",")
                    pos_literals = []
                    log.write(f"Found head: {head} :- {literals}\n")
                    for lit in literals:
                        if "not" not in lit:
                            pos_literals.append(lit.strip())
                        atoms.add(lit.replace("not","").strip())
                transformed_lines.append(f"h({head},{i},({','.join(pos_literals)})) :- {','.join(pos_literals)}, not {head}.")
            for atom in atoms:
                transformed_lines.append(f"#external: {atom}.")
    
        return "\n".join(transformed_lines)

