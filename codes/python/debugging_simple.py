
import numpy

def pythagoras(x,y):
    x = x**2
    y = x**2
    return (x+y)**0.5

a,b = numpy.random.random(2)
c = pythagoras(a, b)
print("a**2 + b**2 == c**2: {a} + {b} == {c}".format(a=a**2,b=b**2,c=c**2))
