#!/usr/bin/env python3

import pylab
import numpy
pylab.ion()
import sys

cores = numpy.arange(1,100,1)
# I want to start from an example case where 95% is spent in comp and 5% in comm,
# e.g. comptime = 95, commtime = 5
compcost = .95
commcost = .05

'''
We want them to start in the same ballpark, even equal, so:

compcost*size**3+commcost*size**2 = compcost/commcost*size

<=>

0.95*size**3+0.05*size**2 - 19*size == 0

<=> 

0.95*size**2+0.05*size - 19 == 0  || do not consider size==0!

<=>

19 size^2 + size - (19)(5)(2)(2) == 0

<=>

size == (-1/19 ± sqrt(1/((19)(19))+(2)(2)(5)(2)(2)))/2 == 4.44

'''

size = 4.5


def comptime(compcost, size):
    return compcost*size**3

def commtime(commcost, size):
    return commcost*size**2

comptime2 = compcost*size**3/8
commtime2 = commcost*size**2/4

comptime4 = compcost*size**3/64
commtime4 = commcost*size**2/16



# comptime/commtime ~ size/cores


#fig=pylab.figure(figsize=(16,9))
#fig.subtitle("Scaling of Computation/Communication")
#ax=fig.add_axes([0.0,0.0,1.0,1.0])
#ax.plot(cores, compcost/commcost*size/cores**(1/3))
#fig.show()

pylab.gcf()
pylab.clf()
pylab.plot(cores, compcost/commcost*size/cores**(1/3), label="Comp/Comm")
#pylab.plot(cores, comptime(compcost,size/cores**(1/3))/commtime(commcost,size/cores**(1/3)))
comptimecores = comptime(compcost,size/cores**(1/3))
commtimecores = commtime(commcost,size/cores**(1/2))
pylab.plot(cores, comptimecores, label="Comp time")
pylab.plot(cores, commtimecores*20, label="Comm time * 20")
pylab.plot(cores, 
           comptimecores+
           commtimecores,
           label="Total time") # total time is ideal as it has only surface and volume in it
pylab.title("Scaling of Computation/Communication")
pylab.legend()
#pylab.savefig("images/domain_decomp_scaling.png")
pylab.savefig(sys.argv[-1])
