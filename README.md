# Wireless Vehicle Network - applications for quantum optimization

Introduction slides are in the repo too! Please download it to obtain futhuer information.
[![Build Status](https://i.ibb.co/sCpw28h/Screen-Shot-2020-09-10-at-1-38-50-AM.png)](https://i.ibb.co/sCpw28h/Screen-Shot-2020-09-10-at-1-38-50-AM.png)
## Usage
1. Please install prerequirements: python 3.X
2. Create a new working environment (optional)
3. type following commands to setup the simulation:
```
git clone https://github.com/koreal6803/Application-of-quantum-optimization
cd Application-of-quantum-optimization
pip install -r requirements.txt
python vis.py
```
## Description
Our tasks are composed of 3 subtasks: sensor distribution, vehicle localization, and data synchrnization.

1. Sensor distriution: Reach approximate solutions of the MAXCUT problem by quantum approximate optimization algorithm (QAOA). Use MAXCUT to distribute the sensors.
2. Vehicle localization: Use the distributed sensors (by the first subtask) to localize vehicles. The problem is equivalent to minimization of quadratic functions.
3. Data synchrnization: design routes from servers to many locations and back to the server. Physically, the problem can be mapped into an Ising Hamiltonian, and we used the existing quantum algorithm to acquire its eigenstates.
