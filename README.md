## Library Dependencies
- pathlib
- heapq
- os
- random

Note: These libraries are local to your Python interpreter; you only have to import them directly.

## Description
**Snake Venom Toxin Inspired A* Algorithm (SVT-A*)**

An algorithm based on the dynamic movement of snake venom within a living organism that is inflicted by it. Using diffusion flux as the main heuristic will mimic how the snake venom moves inside an organism, with a decreasing concentration value affected by time. 

This algorithm is applied in the context of penetration testing, in which it traverses the file directories of your machine and tries to find a path between two directories. This algorithm is made for a Bachelor's thesis. Feel free to improve or use this algorithm in other use cases.

## How to Use this?
```
git pull github_url
```

```
python main.py [args]
```
### The following are the Arguments 
[StartDirectoryPath]: Optional => by default, this is the current directory where the main.py script is

[TargetDirectoryPath]: Required => It needs to be an absolute path to work

[TargetFile]: Required => The file that the algorithm will find.


# Authors:
 Marc Rovic Mapa, John Kenneth Ignacio, and Dominic Reymar Gunio.


