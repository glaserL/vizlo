# vizlo
> ⚠️ **IMPORTANT**: vizlo is no longer maintained. 
> The follow-up tool is called viASP, available here: [glaserL/viasp](https://github.com/glaserL/viasp)⚠️

Vizlo is a visualization extension for [clingo](https://potassco.org/clingo/). 
It is intended to help you visualize and potentially debug programs by showing an 
iterative simulation of the solving process.


## Installation

Vizlo is distributed via [conda-forge](https://conda-forge.org):

`conda install -c conda-forge vizlo`
## Usage
Debuggo wraps itself around the Control object of the clingo python API. We assume you are familiar with the 
[clingo python API](https://potassco.org/clingo/python-api/5.4/).


```python
import vizlo
import matplotlib.pyplot as plt

ctl = vizlo.VizloControl(["0"])
ctl.add("base", [], "{a}. {b}. :- a.")
ctl.ground([("base", [])])
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
Vizlo extends the `clingo.Control` object with two functions, `paint` and `add_to_painter`:

---

`paint(self, atom_draw_maximum=20, show_entire_model=False, sort_program=True, figsize=None, dpi=300, rule_font_size=12, model_font_size=10):`

* Will create a graph visualization of the solving process. If models have been added using add_to_painter,
         only the solving paths that lead to these models will be drawn.
  * `atom_draw_maximum: int = 20`
  The maximum amount of atoms that will be printed for each partial model.            
  * `show_entire_model: bool = False`
     If false, only the atoms that have been added at a solving step will be printed (up to atom_draw_maximum).
     If true, all atoms will always be printed (up to atom_draw_maximum).
  * `sort_program: bool = True`
     If true, the rules of a program will be sorted and grouped by their dependencies.
     Each set of rules will contain all rules in which each atom in its heads is contained in a head.
  * `figsize: Tuple[float, float] = None`
       The figure size the visualization will be set to. If none, vizlo tries to extrapolate a appropriate one.
            default=None
  * `dpi: int = 300`
       The dots per inch ratio for the visualization.
            default=300
  * `rule_font_size: int = 12`
       The font size for the rules.
  * `model_font_size: int = 10`
       The font size for the atoms in the model nodes.

---

`add_to_painter(self, model: Union[Model, PythonModel, Collection[clingo.Symbol]]):`
* will register a stable model with the internal painter. On all consecutive calls to `paint()`, the solving path to this stable model will be painted.
  * `model: Union[Model, Collection[clingo.Symbol]]` : the model to add to the painter.
