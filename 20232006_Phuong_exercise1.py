import math
shape = str(input())
if shape == 's':
    side = float(input())
    print('The area is', '{:.4f}'.format(side**2))
elif shape == 'r':
    l = float(input())
    w = float(input())
    print('The area is', '{:.4f}'.format(l*w))
elif shape == 'c':
    r = float(input())
    print('The area is', '{:.4f}'.format(math.pi*r*r))