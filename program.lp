h(a,1,(b)) :- b, not a.
h(b,2,(c)) :- c, not b.
h(c,3,(d)) :- d, not c.
h(d,4,()) :- not d.
#external a.
#external b.
#external c.
#external d.


#script(python)
import clingo
def main(prg):
	prg.ground([("base", [])]) # What is this?
	#prg.solve()
	with prg.solve(yield_=True) as it:
		for m in it:
			print(type(m))
			print(m.type)
			print(m.is_true(1))
			for sym in m.symbols(atoms=True):
				print(f"Model has symbol: {sym}")
				print(sym.name) 
				print(sym.arguments)
				# for h(d,4,())
			for sym in m.symbols(terms=True):
				print(f"Model has symbol: {sym}")
			for sym in m.symbols(csp=True):
				print(f"Model has symbol: {sym}")
			# And then try to figure 
	print("Adding d..")
	prg.assign_external(clingo.String("d"), True)

	with prg.solve(yield_=True) as it:
		for m in it:
			print(type(m))
			print(m.type)
			print(m.is_true(1))
			for sym in m.symbols(atoms=True):
				print(f"Model has symbol: {sym}")
				print(type(sym))
				print(sym.name) 
			for sym in m.symbols(terms=True):
				print(f"Model has symbol: {sym}")
			for sym in m.symbols(csp=True):
				print(f"Model has symbol: {sym}")
				print(sym.arguments)
#end.