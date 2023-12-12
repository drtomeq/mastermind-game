from mmconstants import *
from random import randrange

def similar_colour(colour1, colour2, tolerance):
    for count, colour1_number in enumerate(colour1):
        if abs(colour1_number - colour2[count])>tolerance:
            return False
    return True

def unique_colour(colour, list, tolerance):
    for other_colour in list:
        if similar_colour(colour, other_colour, tolerance):
           return False
    return True

def random_colour():
    return tuple(randrange(0, 255) for i  in range(3))

def colour_list(tolerance = 100):
    colours = []
    for i in range(NUMBER_OPTIONS):
        while True:
            current_colour =random_colour()
            if unique_colour(current_colour, colours, tolerance):
                break
            else:
                tolerance -= 1
        colours.append(current_colour)
    return colours
