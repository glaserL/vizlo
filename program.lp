h(a,1,(b)) :- b, not a.
h(b,2,(c)) :- c, not b.
h(c,3,(d)) :- d, not c.
h(d,4,()) :- not d.

% Original program.
%a :- b.
%b :- c.
%c :- d.
%d.
