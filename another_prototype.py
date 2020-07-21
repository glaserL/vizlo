import clingo
class Context:
    def h(self, head, id, body):
        return head, id, body

def on_model(m):
    print (m)
ctl = clingo.Control()
# <block>:1:13-15: error: syntax error, unexpected :- ???
ctl.add("base", [], """\
@h(a,1,(b)) :- b, not a.
@h(b,2,(c)) :- c, not b.
@h(c,3,(d)) :- d, not c.
@h(d,4,()) :- not d.
""")
ctl.ground([("base", [])], context=Context())
ctl.solve(on_model=on_model)
