

class ASPTransformer():
    """
    Transforms a given ASP program into a reified version.
    """

    def __init__(self):
        pass

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