import clingo, sys

class Context:
    def h(self, head, id, body):
        return head, id, body

#def match(self, name:str, arity:int) -> bool
def on_model(m):
    print (m)
    print(type(m))
    symbols_in_model = m.symbols(atoms=True,csp=True)
    
    sample_sym = symbols_in_model[0]
    
    args = sample_sym.arguments
    symbols_in_body = args[2].arguments
    head = args[0]
    print(head)
    print(sample_sym.negative)
    print(sample_sym.positive)

program = ""
with open(sys.argv[1], encoding="utf-8") as f:
    program = "".join(f.readlines())

print(f"Read program \n{program}")

ctl = clingo.Control()

ctl.add("base", [], program)


ctl.ground([("base", [])], context=Context())
#ctl.solve(on_model=on_model)
tmp = None
with ctl.solve(yield_=True) as handle:
    for m in handle:
        symbols_in_model = m.symbols(atoms=True,csp=True)
        sample_sym = symbols_in_model[0]
        args = sample_sym.arguments
        head = args[0]
        tmp = head
        #ctl.assign_external(clingo.String("d"),True)

ctl.assign_external(head,True)
ctl.solve(on_model=on_model)

# @h(a,1,(b)) :- b, not a.
# @h(b,2,(c)) :- c, not b.
# @h(c,3,(d)) :- d, not c.
# @h(d,4,()) :- not d.



# Maybe an issue? : 
# Model objects cannot be constructed from Python. Instead they are obained during solving (see Control.solve()). Furthermore, the lifetime of a model object is limited to the scope of the callback it was passed to or until the search for the next model is started. They must not be stored for later use.