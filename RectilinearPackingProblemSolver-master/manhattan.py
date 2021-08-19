from math import *
 
def m_dist(x, y):
    return sum(abs(a - b) for a, b in zip(x, y))
 
print ("(1)", m_dist([2,2], [1,7]))
print ("(2)", m_dist([5,2], [12,8]))
print ("(3)", m_dist([2,2], [5,2]))

print ("(4)", m_dist([3,2], [2,2]))
print ("(5)", m_dist([2,0], [2,0]))