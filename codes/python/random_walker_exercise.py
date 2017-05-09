import numpy
minx,maxx,miny,maxy = 0,9,0,9
persons = {"A": (minx,miny),
           "B": (maxx,maxy)}
while (persons["A"] != persons["B"]):
    xs = numpy.random.randint(minx,maxx+1,2)
    ys = numpy.random.randint(miny,maxy+1,2)
    persons["A"]=(xs[0],ys[0])
    persons["B"]=(xs[1],ys[1])
print("Persons A and B bumped to each other at {}.".format(str(persons["A"])))
