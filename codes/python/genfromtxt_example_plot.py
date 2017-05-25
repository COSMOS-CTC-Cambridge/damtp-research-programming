plotfilename="../files/matplotlib-3d-example.png"
infile = "../files/genfromtxt_example_data.txt"
oufile = "../files/genfromtxt_example_plot.png"
import numpy
import matplotlib
import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D

def randrange(n, vmin, vmax):
    return (vmax - vmin)*numpy.random.rand(n) + vmin

data = numpy.genfromtxt(infile, comments="#", delimiter="\t", skip_header=3)
fig = matplotlib.pyplot.figure()
ax = fig.add_subplot(111, projection='3d')
n = data.shape[0]
# plot a sphere for each particle
# colour charged particles red (charge>0), blue (charge<0) and neutrals green
blues = data[data[:,7]<0]
reds = data[data[:,7]>0]
greens=data[numpy.logical_not(numpy.logical_or(data[:,7]<0,data[:,7]>0))]
ax.scatter(blues[:,0], blues[:,1], blues[:,2], c="b", edgecolors="face",
           marker="o", s=blues[:,6])
ax.scatter(reds[:,0], reds[:,1], reds[:,2], c="r", edgecolors="face",
           marker="o", s=greens[:,6])
ax.scatter(greens[:,0], greens[:,1], greens[:,2], c="g", edgecolors="face",
           marker="o", s=greens[:,6])
ax.quiver(blues[:,0], blues[:,1], blues[:,2], blues[:,3], blues[:,4],
          blues[:,5], pivot="tail")
ax.quiver(reds[:,0], reds[:,1], reds[:,2], reds[:,3], reds[:,4],
          reds[:,5], pivot="middle")
ax.quiver(greens[:,0], greens[:,1], greens[:,2], greens[:,3], greens[:,4],
          greens[:,5], pivot="tip")
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
matplotlib.pyplot.savefig(oufile)
print(oufile, end="")
