import numpy as np


def angle_range(a: float) -> float:
    """Return an angle within the range [-pi, pi]."""
    while a < -np.pi:
        a += 2 * np.pi
    while a > np.pi:
        a -= 2 * np.pi
    return a


def angle_diff(a: float, b: float) -> float:
    """Get the shortest distance between 2 angles."""
    a = angle_range(a)
    b = angle_range(b)
    diff = angle_range(a - b)
    return diff


##########
# length #
##########
meters = 1
m = meters

feet = 0.3048
ft = feet
to_feet = 1 / feet
to_ft = to_feet

inches = 0.0254
to_inches = 1 / inches

centimeters = 0.01
cm = centimeters
to_centimeters = 1 / centimeters
to_cm = centimeters

milimeters = 0.001
mm = milimeters
to_milimeters = 1 / milimeters
to_mm = to_milimeters

#########
# angle #
#########
radians = 1

degrees = 0.0174533
to_degrees = 1 / degrees

########
# mass #
########
kilograms = 1
kg = kilograms

grams = 0.001
g = grams
to_grams = 1 / grams
to_g = to_grams

pounds = 0.453592
lbs = pounds
to_pounds = 1 / pounds
to_lbs = to_pounds

########
# time #
########
seconds = 1
s = 1

minutes = 60
min = minutes
to_minutes = 1 / minutes
to_min = to_minutes

milliseconds = 0.001
ms = milliseconds
to_milliseconds = 1 / milliseconds
to_ms = to_milliseconds

milliseconds_100 = 0.1
ms_100 = milliseconds_100
to_milliseconds_100 = 1 / milliseconds_100
to_ms_100 = to_milliseconds_100

##########
# voltage #
###########
volts = 1
