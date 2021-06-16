CONTENTS OF THIS FILE
---------------------

 * Introduction
 * Scenario
 * Version

INTRODUCTION
------------

This program is a Python written implementation of the **Simulated Annealing** algorithm as a solution to a [Vehicle Routing Problem](https://en.wikipedia.org/wiki/Vehicle_routing_problem)
with Time Constraints (VRPTW), a generalization of the Travelling Salesman Problem. There is an included sample dataset of packages to be delivered to
customers along with a distance table. The purpose of the algorithm is to create a route with a near optimal order of
packages to be delivered by keeping the total mileage of the route as low as possible, while still ensuring the packages
all meet their requirements including: delivery deadlines, wrong address changes, and packages delayed to the HUB.

SCENARIO
--------

WGUPS needs to determine an efficient route and delivery distribution for their Daily Local Deliveries (DLD) because
packages are not currently being consistently delivered by their promised deadline. The Salt Lake City DLD route has
three trucks, two drivers, and an average of 40 packages to deliver each day. Each package has specific criteria and
delivery requirements.

VERSION
-------

Application Version: 1.0

Python 3.8.5

PyCharm 2021.1.2 (Community Edition)
Build #PC-211.7442.45, built on June 1, 2021
Runtime version: 11.0.11+9-b1341.57 amd64
VM: Dynamic Code Evolution 64-Bit Server VM by JetBrains s.r.o.
Windows 10 10.0
GC: G1 Young Generation, G1 Old Generation
Memory: 2042M
Cores: 4
