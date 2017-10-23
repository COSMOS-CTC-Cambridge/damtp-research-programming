def make_counter(start):
    next_value = start
    def next():
        nonlocal next_value
        val = next_value
        next_value += 1
        return val
    return next

my_first_counter = make_counter(0)
my_second_counter = make_counter(0)
my_third_counter = make_counter(2)
print(my_first_counter())
print(my_second_counter())
print(my_third_counter())
print(my_first_counter())
print(my_second_counter())
print(my_first_counter())
print(my_second_counter())
print(my_second_counter())
print(my_first_counter())
print(my_first_counter.__closure__[0].cell_contents)
