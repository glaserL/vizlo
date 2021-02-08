# vizlo
Vizlo is a visualization extension for [clingo](https://potassco.org/clingo/). 
It is intended to help you visualize and potentially debug programs by showing an 
iterative simulation of the solving process.


## Installation

Vizlo is distributed over pypi:
```
pip install vizlo
```

## Usage
Debuggo wraps itself around the Control object of the clingo python API. We assume you are familiar with the 
[clingo python API](https://potassco.org/clingo/python-api/5.4/).


```python
import vizlo
import matplotlib.pyplot as plt

ctl = vizlo.VizloControl()
ctl.add("base", [], "{a}. {b}. :- a.")
ctl.ground([("base", [])])
with ctl.solve(yield_=True) as handle:
    for m in handle:
        if len(m) > 1:
            ctl.add_to_painter(m)

ctl.paint()
plt.show()
```

# Example
The resulting output is a visualization like the one below. Vizlo sorts the statements of a given logic
program by their dependencies. That way we can simulate an iterative solving flow. Recursions and sets of rules that an 
atom depends on are merged together into one solving step (one line in the graphic.) 

```
{a}.
{b}.
:- a.
```
---
![Example Program](docs/img/sample.png "Sample solver tree")

# API
Vizlo extends the `clingo.Control` object with two functions:



