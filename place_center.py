import sympy
from scipy.optimize import fsolve
import numpy as np

def place_center(P, l):
    RR = ((l / 2) / np.pi) ** 2
    R0 = (P[0, :] + P[1, :] + P[2, :]) / 3

    def F(x):
        return [(x[0] - P[0][0]) ** 2 + (x[1] - P[0][1]) ^ 2 + (x[2] - P[0][2]) ** 2 - RR, (
            x[0] - P[1][0] ** 2 + (x[1] - P[1][1]) ** 2 + (x[2] - P[1][2]) ** 2 - RR,
            (x[0] - P[2][0]) ** 2 + (x[1] - P[2][1]) ** 2 + (x[2] - P[2][2]) ** 2 - RR)]

    res = fsolve(F, R0)
    return res
