import math
import matplotlib.pyplot as plt
import numpy as np

print(np.sqrt(16))
print(math.sqrt(16))


x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.show()


### THis si added to see how the branches are branching and merging works