import pylab as pl
import numpy as np
import matplotlib.pyplot as plt
import mpld3

y=['Components', 'Drivers view of the road', 'Tread depth', 'Rbt', 'Lighting and signalling', 'Rbt (sp)', 'Wheel bearings', 'Hub components', 'Suspension arms',
 'Fuel and exhaust']
x=[308, 296, 264, 196, 192, 188, 176, 164, 164, 156]
x.reverse()
y.reverse()
fig = plt.figure()

width = .75
ind = np.arange(len(x))
plt.barh(ind, x)
plt.yticks(ind + width / 2, y)
fig.tight_layout()

figure_html=mpld3.fig_to_html(fig)
with open("fig.html", "w") as html_file:
	html_file.write(figure_html)
	#print(figure_html, html_file)
#print(figure_html)
plt.savefig("figure.pdf")

#ax = pl.subplot(111)
#ax.bar(x, y, width=100)

