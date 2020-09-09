import itertools
import random
import numpy as np

def generate_problem(node, sensors, radius):
  problem = []
  for s in sensors:
    d = ((node.x - s.x) ** 2 + (node.y - s.y) ** 2) ** 0.5 + np.random.normal() * 5
    if d < radius:
      problem.append((d, s.x, s.y))
  return problem


def solve_mathmatically(problems, DX, DY):

  problem_level2 = []
  for p1, p2 in itertools.combinations(problems, r=2):
    d1, x1, y1 = p1
    d2, x2, y2 = p2

    problem_level2.append((x1 - x2, y1 - y2, -0.5*(d1**2-d2**2-x1**2+x2**2-y1**2+y2**2)))


  final_result = []
  for p1, p2 in itertools.combinations(problem_level2, r=2):

    a, b, c = p1
    d, e, f = p2

    if a*e - b*d == 0 or b*d - a*e == 0:
      continue

    x =  (c*e - b*f) / (a*e - b*d)
    y = (c*d - a*f) / (b*d - a*e)
    final_result.append((x // DX, y // DY, x, y))
  return final_result

from qiskit import BasicAer
from qiskit.aqua.algorithms import QAOA, NumPyMinimumEigensolver
from qiskit.optimization.algorithms import MinimumEigenOptimizer, RecursiveMinimumEigenOptimizer
from qiskit.optimization import QuadraticProgram


def qubo_optimization(position_candidates, method='classical'):
  qubo = QuadraticProgram()
  qubo.binary_var(name='x0')
  qubo.binary_var(name='x1')
  qubo.binary_var(name='x2')
  qubo.binary_var(name='x3')
  qubo.binary_var(name='x4')
  qubo.binary_var(name='x5')
  qubo.binary_var(name='y0')
  qubo.binary_var(name='y1')
  qubo.binary_var(name='y2')
  qubo.binary_var(name='y3')
  qubo.binary_var(name='y4')
  qubo.binary_var(name='y5')
  a = 0
  b = 0
  aa = 0
  bb = 0
  RR = 0
  for sensor in position_candidates:
      a = a + sensor[0]
      b = b + sensor[1]
      aa = aa + sensor[0] * sensor[0]
      bb = bb + sensor[1] * sensor[1]
  #   RR = RR + sensor[2] * sensor[2]

  #print('a=',a)
  #print('b=',b)
  #print('aa=',aa)
  #print('bb=',bb)
  #print('RR=',RR)

  N=len(position_candidates)
  #print('N=',N)

  #np.array
  #a=5
  #b=7
  #R=13
  lx0=-2*a
  lx1=-4*a
  lx2=-8*a
  lx3=-16*a
  lx4=-32*a
  lx5=-64*a
  ly0=-2*b
  ly1=-4*b
  ly2=-8*b
  ly3=-16*b
  ly4=-32*b
  ly5=-64*b
  #qubo.binary_var('y')
  #qubo.binary_var('z')
  qubo.minimize(constant=aa+bb,
              linear=[lx0,lx1,lx2,lx3,lx4,lx5,ly0,ly1,ly2,ly3,ly4,ly5],
              quadratic={('x0', 'x0'): 1*N, ('x1', 'x1'): 4*N, ('x2', 'x2'): 16*N,('x3', 'x3'): 64*N,('x4', 'x4'): 256*N,('x5', 'x5'): 1024*N,
                                      ('x0', 'x1'): 4*N,('x0', 'x2'): 8*N,('x0', 'x3'): 16*N,('x0', 'x4'): 32*N,('x0', 'x5'): 64*N,
                                      ('x1', 'x2'): 16*N,('x1', 'x3'): 32*N,('x1', 'x4'): 64*N,('x1', 'x5'): 128*N,
                                      ('x2', 'x3'): 64*N,('x2', 'x4'): 128*N,('x2', 'x5'): 256*N,
                                      ('x3', 'x4'): 256*N,('x3', 'x5'): 512*N,
                                      ('x4', 'x5'): 1024*N,
                          ('y0', 'y0'): 1*N, ('y1', 'y1'): 4*N, ('y2', 'y2'): 16*N,('y3', 'y3'): 64*N,('y4', 'y4'): 256*N,('y5', 'y5'): 1024*N,
                          ('y0', 'y1'): 4*N,('y0', 'y2'): 8*N,('y0', 'y3'): 16*N,('y0', 'y4'): 32*N,('y0', 'y5'): 64*N,
                          ('y1', 'y2'): 16*N,('y1', 'y3'): 32*N,('y1', 'y4'): 64*N,('y1', 'y5'): 128*N,
                          ('y2', 'y3'): 64*N,('y2', 'y4'): 128*N,('y2', 'y5'): 256*N,
                          ('y3', 'y4'): 256*N,('y3', 'y5'): 512*N,
                          ('y4', 'y5'): 1024*N
                          })
  if method == 'qaoa':
    qaoa_mes = QAOA(quantum_instance=BasicAer.get_backend('statevector_simulator'))
    qaoa = MinimumEigenOptimizer(qaoa_mes)   # using QAOA
    result = qaoa.solve(qubo)
  else:
    exact_mes = NumPyMinimumEigensolver()
    exact = MinimumEigenOptimizer(exact_mes)  # using the exact classical numpy minimum eigen solver
    result = exact.solve(qubo)

    dX=0
    dY=0
    for i, x in enumerate(result.x):
      if i < len (result.x)/2:
        dX = dX + x * 2 ** (i%6)
      else:
        dY = dY + x * 2 ** (i%6)
  return dX,dY

def localize(problems, DX, DY):
  position_candidates = solve_mathmatically(problems, DX, DY)

  if len(position_candidates) >= 2:
    x, y = qubo_optimization(position_candidates, method='classical')
  elif len(position_candidates) == 1:
    return position_candidates[0], position_candidates[1]
  elif len(position_candidates) == 0:
    return -100, -100
  return x * DX, y * DY
