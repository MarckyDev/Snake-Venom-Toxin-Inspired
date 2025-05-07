
## Description
**Venom-Inspired Pathfinding Enhancement of A* (VIPER)**

An algorithm based on the dynamic movement of snake venom within a living organism that is inflicted by it. Using diffusion flux as the main heuristic will mimic how the snake venom moves inside an organism, with a decreasing concentration value affected by time. 

This algorithm is applied in the context of penetration testing, in which it traverses the file network of your machine and tries to find a path between two directories. This algorithm is made for a Bachelor's thesis. Feel free to improve or use this algorithm in other use cases.

This repository is a collection of benchmarked algorithms used for testing of VIPER. the scripts will create a file of results from every algorithm within the script's directory.

### How to Use this?

## The following are the Arguments 
```
[-sp] StartDirectoryPath: Optional => by default, this is the current directory where the main.py script is located. It can also be an absolute path to a directory

[-tp] TargetDirectoryPath: Required => An absolute path that the algorithm will find

[-tf] TargetFile: Required => The file that the algorithm will find that is within the target directory path.

[-alg] Algorithms: Optional => The default option is "all" it contains a list of algorithms that you can run.
```

Clone the repository
```
git clone https://github.com/MarckyDev/Snake-Venom-Toxin-Inspired.git
```

You may opt-out on using the "-sp" command

```
python main.py -tp "absolute/path/to/target/directory" -tf "filename.extension"
```

You may also opt-out on using the "-alg" command to run everything
```
python main.py -sp "absolute/path/to/starting/directory" -tp "absolute/path/to/target/directory" -tf "filename.extension"
```




# Authors:
 Marc Rovic Mapa, John Kenneth Ignacio, and Dominic Reymar Gunio.


