#program base.
h(a,1,(b,)) :- b; not a.
h(b,2,(c,)) :- c; not b.
h(c,3,(d,)) :- d; not c.
h(d,4,()) :- not d.
#external d.
#external c.
#external b.
#external a.