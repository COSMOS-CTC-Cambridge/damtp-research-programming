
def bottom_func(x):
    y = x**2
    return str(x) + " squared equals " + str(y)

def top_func(z):
    result = bottom_func(z)
    return result
        
top_func("7")
