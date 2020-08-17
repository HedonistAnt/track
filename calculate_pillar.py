from pymap3d import ecef2enu, enu2ecef, ecef2geodetic
import numpy as np
from planar_pos import planar_pos
from place_center import place_center
def calculate_pillar(P_h, P_2, P_f, L_h,L_2, l, elevation,upper_point,max_dist):
    F = ecef2geodetic(P_h[0], P_h[1], P_h[2])
    [hor1, hor2, hor3] = ecef2enu(P_h[0], P_h[1], P_h[2], F[0], F[1], F[2])
    [p2_1, p2_2, p2_3] = ecef2enu(P_2[0], P_2[1], P_2[2], F[0], F[1], F[2])

    hor3 = hor3 - 0.09952
    p2_3 = p2_3 - 0.09952

    dH = abs(hor3 - p2_3)


    L2_h = [np.sqrt(x**2 - dH**2) for x in  L_2]

    R1 = [planar_pos(hor1, hor2, p2_1, p2_2, [L_h[0], L2_h[0]], max_dist), hor3]
    R2 = [planar_pos(hor1, hor2, p2_1, p2_2, [L_h[1], L2_h[1]], max_dist), hor3]
    R3 = [planar_pos(hor1, hor2, p2_1, p2_2, [L_h[2], L2_h[2]], max_dist), hor3]
    C = place_center([R1, R2, R3], l)

    [a, b, c] = enu2ecef(C(1), C(2), C(3) - np.mean(elevation), F[0], F[1], F[2])
    center = [a, b, c];

    Hl = np.linalg.norm(np.array([hor1, hor2, hor3]) - C)

    h = np.mean(elevation) + np.sqrt(upper_point**2 - Hl ** 2)


    return center,h


