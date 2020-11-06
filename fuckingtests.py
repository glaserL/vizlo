from debuggo.main import Dingo


ctl = Dingo()
print(ctl)

ctl.add("base", [], "a :- b.\nb.", )
print(ctl)
ctl.ground([("base", [])])
sat = ctl.solve()
from matplotlib import pyplot as plt
pic = ctl.paint(None)
plt.imshow(pic)
plt.show()