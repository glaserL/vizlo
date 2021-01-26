# debuggo
Debuggo is a visualization extension for the clingo solver TODO link.
Using clingo you can visualize the solving of a program in an iterative way.
For an indepth manual you can look at the paper LINK

## Installation


## Usage
Debuggo wraps itself around the clingo.Control object. You can use this object just like you would
use the normal clingo control object.

```python
import debuggo
import matplotlib.pyplot as plt

ctl = debuggo.main.Debuggo()
ctl.add("base", [], "a. a :- b.")
ctl.ground([("base", [])])
with ctl.solve(yield_=True) as handle:
    for m in handle:
        if len(m) > 1:
            ctl.add_to_painter(m)

ctl.paint()
plt.show()
```
TODO: Put the resulting image here!
