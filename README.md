# debuggo
Debugging module for clingo

## Rough idea as of now:
* Reify a given clingo program to enable step-wise execution
* Execute the program and record a "solver history", currently it's just a path but with choice rules etc. we get a tree.
* Visualize this in some way.


# Approach
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    for model in ctl.solve(_yield=True):
        if model.hasSomeThingSpecial():
            ctl.addToPainter(model)
            # TODO 1: Paint all of them nicely
            # TODO 2: Paint one or some of them
            # TODO 3: Handle recursion with special input
            # TODO 4: Resort them based on dependency
            # TODO 5: Handle recursion without special input

        ctl.paintModels()
    img = ctl.paint()
    ctl._show(img)
