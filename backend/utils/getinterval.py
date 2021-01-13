import math 

def getinterval(flow):
    acc_internal = 0
    for i in range(len(flow) - 1):
        acc_internal += math.sqrt(math.pow(abs(flow[i][1] - flow[i+1][1]), 2) + math.pow(abs(flow[i][2] - flow[i+1][2]), 2))
    return acc_internal