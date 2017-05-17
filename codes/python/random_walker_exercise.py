import numpy

class locus:
    '''This class has no unit tests: please add some!'''
    def __init__(self, locus):
        self.x = locus[0]
        self.y = locus[1]
    def __eq__(self, other):
        '''This tells python how to determine if two instances of this class are "equal".'''
        return self.x==other.x and self.y==other.y
    def __repr__(self):
        return "[{x},{y}]".format(x=self.x,y=self.y)

class walker:
    '''This class has no unit tests: please add some!'''
    def __init__(self, l):
        self.locus=locus(l)
    def take_step(self, locus):
        self.locus = locus

class random_walker(walker):
    '''This class has no unit tests: please add some!'''
    def try_step(self):
        '''Take a random unit step along an axis. The algorithm simply picks a direction using a random integer in
        [0,3] where numbers > 1.5 move to right/up and numbers < 1.5 move left/down; even numbers refer to x
        and odd ones to y axis.
        N.B. There are no ifs and there is no modular arithmetic: both are poison for modern CPU perfomance.'''
        res = numpy.random.randint(4)
        x,y = self.locus.x, self.locus.y
        x = x + ((res+1) & 0x1)*(res-1)
        y = y + ((res) & 0x1)*(res-2)
        return locus((x,y))

# define the dimensions of the box to walk in
minx,maxx,miny,maxy = 0,19,0,19
# define two walkers starting from diagonally opposite corners
persons = {"A": random_walker((minx,miny)),
           "B": random_walker((maxx,maxy))}
while not(persons["A"].locus == persons["B"].locus):
    for name in persons:
        '''Think about why I do "name in persons" and not "name in persons.values()" or "name in
        persons.items()"!
        What if the list was 1e9 elements long?'''
        loc = persons[name].try_step()
        while not((minx <= loc.x <= maxx) and (miny <= loc.y <= maxy)):
            loc = persons[name].try_step()
        persons[name].take_step(loc)
    print("Persons A is at {:7} and person B at {:7}".format(persons["A"].locus, persons["B"].locus))
print("Persons A and B bumped to each other at {}.".format(str(persons["A"].locus)))
