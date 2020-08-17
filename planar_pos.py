from sympy import solve_poly_system,symbols
import numpy as np
def planar_pos(x1,y1,x2,y2,L,min_norm):
    x,y = symbols('x y')
    solution = solve_poly_system([(x-x1)**2 + (y-y1)**2 - L[0]**2, (x-x2)**2 + (y-y2)**2 - L[1]**2])
    Xres = [solution[0][0], solution[1][0]]
    Yres = [solution[0][1],solution[1][0]]
    print(solution[0])
    norm_vector = [np.linalg.norm(np.array([solution[0][0],solution[0][1]],dtype= np.float64)), np.linalg.norm(np.array([solution[1][0],solution[1][1]],dtype= np.float64))]

    if min_norm:
        i=norm_vector.index(min(norm_vector))
    else:
        i=norm_vector.index(max(norm_vector))
    return [Xres[i], Yres[i]]

if __name__ == "__main__":
    planar_pos(8,8, 10,10,[12,12],True)