from typing import List
import numpy as np
import networkx as nx

from qiskit import Aer
from qiskit.tools.visualization import plot_histogram
from qiskit.circuit.library import TwoLocal
from qiskit.optimization.applications.ising import max_cut, tsp
from qiskit.aqua.algorithms import VQE, NumPyMinimumEigensolver
from qiskit.aqua.components.optimizers import SPSA
from qiskit.aqua import QuantumInstance
from qiskit.optimization.applications.ising.common import sample_most_likely
from qiskit.optimization.algorithms import MinimumEigenOptimizer
from qiskit.optimization.converters import IsingToQuadraticProgram
from qiskit.optimization.problems import QuadraticProgram
import random

# setup aqua logging
# import logging from qiskit.aqua import set_qiskit_aqua_logging
# set_qiskit_aqua_logging(logging.DEBUG)  # choose INFO, DEBUG to see the log

class Localization():
    def answer(self, num_det, w_ori: List):
        w = w_ori.copy()
        # determine the place to put the first detector
        n = len(w_ori)
        ans_set = [0 for i in range(n)]
        deg = np.zeros(n)
        for i in range(n):
            deg[i] = sum(w[i])

        max_deg_idx = np.argmax(deg)
        ans_set[max_deg_idx] = 1

        # remove the first detector
        for i in range(n):
            if(w[max_deg_idx][i] == 1):
                w[max_deg_idx][i] == 0
                w[i][max_deg_idx] == 0

        #self.Show_Graph(ans_set, w_ori)

        # select the remaining senor's location
        for i in range(num_det - 1):
            result = self.Qmax_cut(w, ans_set)
            ans_set = self.put_sensor(result, w, ans_set)
#             print('ans_set = ', ans_set)
            #self.Show_Graph(ans_set, w_ori)
        return ans_set

    def Show_Graph(self, ans_set:List, w:List):
        n= len(ans_set) # Number of nodes in graph
        G =nx.Graph()
        G.add_nodes_from(np.arange(0,n,1))

        elist = []
        for i in range(n):
            for j in range(n):
                if(w[i][j] == 1):
                    elist += [(i, j, 1.0)]

        # tuple is (i,j,weight) where (i,j) is the edge
        G.add_weighted_edges_from(elist)
        # update graph
        colors = ['b' if ans_set[i] == 1 else 'r' for i in range(n)]
        pos = nx.spring_layout(G)
        default_axes = plt.axes(frameon=True)
        nx.draw_networkx(G, node_color=colors, node_size=600, alpha=.8, ax=default_axes, pos=pos)
        plt.show()



    ## function for max-cut
    def Qmax_cut(self, w: List[List[int]], ans_set)->List:
        qubitOp, offset = max_cut.get_operator(w)

        # mapping Ising Hamiltonian to Quadratic Program
        qp = QuadraticProgram()
        qp.from_ising(qubitOp, offset)
        qp.to_docplex()#.prettyprint()

        # solving Quadratic Program using exact classical eigensolver
        exact = MinimumEigenOptimizer(NumPyMinimumEigensolver())
        result = exact.solve(qp)

        return result


    def put_sensor(self, result: List, w: List[List[int]], ans_set)->List:
        # select next locality
        n = len(w)
        deg = np.zeros(n)
        for i in range(n):
            deg[i] = sum(w[i])

        buf = -1
        buf_idx = -1
        for i in range(n):
            if(result[i] == 1 and ans_set[i] == 0):
                if(deg[i] > buf):
                    buf = deg[i]
                    buf_idx = i

        to_be_remove_idx = buf_idx


        # update w-list, ans_set
        for i in range(n):
            w[to_be_remove_idx][i] = 0
            w[i][to_be_remove_idx] = 0

        ans_set = [1 if (i == to_be_remove_idx or ans_set[i] == 1) else 0 for i in range(n)]

        return ans_set

def distance(node1, node2):
    return ((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2) ** 0.5

def create_adjacent_matrix(sensors, RADIUS):
    n = len(sensors)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i <= j:
                continue
            if distance(sensors[i], sensors[j]) < RADIUS:
                matrix[i, j] = 1
                matrix[j, i] = 1
    return matrix

def activate_sensors(sensors, RADIUS):
    w = create_adjacent_matrix(sensors, RADIUS)
    s = Localization()
    # number of detectors
    num_det = int(len(sensors) * 0.6)
    return s.answer(num_det, w)

