import math

# every base function is normalized to an amplitude of 1 and a frecuency of 1
# they are only valid if the input is clamped between 0 and 1

def norm_sin(x):
    x = x % 1
    return math.sin(2*math.pi*x)/2

def norm_sqr(x):
    x = x % 1
    if (x < 0.5):
        return 0.5
    else:
        return -0.5

def norm_triang(x):
    x = x % 1
    if x < 0.5:
        return 2*x - 0.5
    else:
        return 1.5 - 2*x
    
def norm_exp(x):
    x = x % 1
    x = x - 1/2
    if x < 0:
        return math.exp(5*x)
    else:
        return math.exp(-5*x)
    