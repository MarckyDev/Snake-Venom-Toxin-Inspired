import os
from os.path import normpath
from pathlib import Path
import time
import threading
from Utils.FileProcessing import FileProcessing
from Utils.PathingUtil import file_limit_reached
from Utils.Metrics import results_in_file


class EBS:
    def __init__(self, start_node, end_node, target_file, file_limit=None, run_time_min=0):
        self.start_node = normpath(start_node)
        self.end_node = normpath(end_node)
        self.target_file = target_file
        self.file_limit = file_limit
        self.run_time_min = run_time_min
        self.stop_event = threading.Event()
        
        # Metrics
        self.infected_nodes = 0
        self.infected_files = 0
        self.start_time = 0
        self.logged_limits = []
        
        # Data structures
        self.blocked_directories = set()
        self.processed_files = set()
        
        # Path reconstruction
        self.forward_parents = {}
        self.backward_parents = {}
        self.intersection_node = None
        self.target_found = False

    def _timer_wrapper(self):
        """Timer thread that sets stop_event after specified minutes"""
        time.sleep(self.run_time_min * 60)
        self.stop_event.set()

    def _infect_directory(self, dir_path):
        """Count files in directory while tracking metrics"""
        try:
            dir_path = normpath(dir_path)
            if dir_path in self.blocked_directories:
                return

            self.blocked_directories.add(dir_path)
            self.infected_nodes += 1

            for f in os.listdir(dir_path):
                file_path = os.path.join(dir_path, f)
                if os.path.isfile(file_path) and file_path not in self.processed_files:
                    self.processed_files.add(file_path)
                    self.infected_files += 1
                    
                    # Check file limits if specified
                    if self.file_limit:
                        for limit in self.file_limit:
                            if (limit not in self.logged_limits and 
                                file_limit_reached(self.infected_files, limit)):
                                self._log_results(limit)

        except Exception as e:
            print(f"Error in {dir_path}: {str(e)}")

    def heuristic(self, current, target):
        """Basic heuristic using file count difference"""
        return abs(FileProcessing().count_files_in_directory(current) - 
                  FileProcessing().count_files_in_directory(target))

    def get_neighbors(self, node):
        """Get accessible directories with file counts and status"""
        try:
            neighbors = FileProcessing().get_all_directories_with_file_counts(node)
            for neighbor in neighbors:
                neighbor["dir_name"] = normpath(neighbor["dir_name"])
            return neighbors
        except PermissionError:
            print(f"Access denied to {node}. Skipping.")
            return []
        except Exception as e:
            print(f"Error getting neighbors for {node}: {str(e)}")
            return []

    def search(self, node, open_list, close_list, parents, is_forward):
        """Expand node and add neighbors to open list"""
        neighbors = self.get_neighbors(node)
        goal = self.end_node if is_forward else self.start_node

        for neighbor in neighbors:
            dir_name = neighbor["dir_name"]
            status = neighbor["status"]

            if dir_name not in close_list and not any(n[0] == dir_name for n in open_list):
                if dir_name in self.blocked_directories:
                    continue

                g = FileProcessing().count_files_in_directory(node) + 1
                h = self.heuristic(dir_name, goal)
                f = g + h
                open_list.append((dir_name, g, h, f))
                parents[dir_name] = node

                if status == "vulnerable":
                    self._infect_directory(dir_name)

    def _check_intersection(self, node_s, node_e, CLOSE_LIST_1, CLOSE_LIST_2):
        """Check if searches have intersected"""
        # Direct node intersection
        if node_s in CLOSE_LIST_2:
            self.intersection_node = node_s
            return True
        if node_e in CLOSE_LIST_1:
            self.intersection_node = node_e
            return True
        
        # Check if neighbors intersect
        neighbors_s = {n["dir_name"] for n in self.get_neighbors(node_s)}
        neighbors_e = {n["dir_name"] for n in self.get_neighbors(node_e)}
        
        # Check if any neighbors are in opposite close lists
        for neighbor in neighbors_s:
            if neighbor in CLOSE_LIST_2:
                self.intersection_node = neighbor
                return True
                
        for neighbor in neighbors_e:
            if neighbor in CLOSE_LIST_1:
                self.intersection_node = neighbor
                return True
        
        # Check if neighbors overlap between searches
        intersection = neighbors_s & neighbors_e
        if intersection:
            self.intersection_node = intersection.pop()
            return True
            
        return False

    def _initialize_search(self):
        """Initialize search data structures"""
        # Initialize timer if needed
        if self.run_time_min > 0:
            timer_thread = threading.Thread(target=self._timer_wrapper)
            timer_thread.daemon = True
            timer_thread.start()

        # Initialize open and close lists
        OPEN_LIST_1 = [(self.start_node, 0, self.heuristic(self.start_node, self.end_node), 0)]
        OPEN_LIST_2 = [(self.end_node, 0, self.heuristic(self.end_node, self.start_node), 0)]
        CLOSE_LIST_1 = set()
        CLOSE_LIST_2 = set()
        
        # Initialize parent pointers
        self.forward_parents = {self.start_node: None}
        self.backward_parents = {self.end_node: None}
        
        return OPEN_LIST_1, OPEN_LIST_2, CLOSE_LIST_1, CLOSE_LIST_2

    def _log_results(self, limit=None):
        """Log results to file"""
        path = self._reconstruct_path()
        results_in_file(
            path,
            self.target_found,
            time.perf_counter() - self.start_time,
            self.infected_nodes,
            self.infected_files,
            "Enhanced_Bidirectional_Search",
            limit or self.file_limit
        )
        if limit:
            self.logged_limits.append(limit)

    def execute(self):
        """Main EBS algorithm execution"""
        self.start_time = time.perf_counter()
        OPEN_LIST_1, OPEN_LIST_2, CLOSE_LIST_1, CLOSE_LIST_2 = self._initialize_search()

        while OPEN_LIST_1 and OPEN_LIST_2 and not self.stop_event.is_set():
            # Check file limits if specified
            if self.file_limit:
                for limit in self.file_limit:
                    if (limit not in self.logged_limits and 
                        file_limit_reached(self.infected_files, limit)):
                        self._log_results(limit)

            # Forward search step
            if OPEN_LIST_1:
                node_s = min(OPEN_LIST_1, key=lambda x: x[3])
                OPEN_LIST_1.remove(node_s)
                node_s = node_s[0]
                CLOSE_LIST_1.add(node_s)

                self.search(node_s, OPEN_LIST_1, CLOSE_LIST_1, self.forward_parents, True)

            # Backward search step
            if OPEN_LIST_2:
                node_e = min(OPEN_LIST_2, key=lambda x: x[3])
                OPEN_LIST_2.remove(node_e)
                node_e = node_e[0]
                CLOSE_LIST_2.add(node_e)

                self.search(node_e, OPEN_LIST_2, CLOSE_LIST_2, self.backward_parents, False)

            # Check for intersection
            if (self._check_intersection(node_s, node_e, CLOSE_LIST_1, CLOSE_LIST_2) or
                node_s == self.end_node or node_e == self.start_node):
                self.target_found = True
                break

        # Final results logging
        self._log_results()
        path = self._reconstruct_path()
        return [path, self.infected_files, self.infected_nodes]

    def _reconstruct_path(self):
        """Reconstruct the complete path from both directions"""
        if not self.intersection_node:
            return []

        # Reconstruct forward path
        forward_path = []
        current = self.intersection_node
        while current is not None:
            forward_path.append(current)
            current = self.forward_parents.get(current)
        forward_path.reverse()

        # Reconstruct backward path (excluding intersection node)
        backward_path = []
        current = self.backward_parents.get(self.intersection_node)
        while current is not None:
            backward_path.append(current)
            current = self.backward_parents.get(current)

        return forward_path + backward_path

    def smooth_path(self, path):
        """Simplify path by removing unnecessary intermediate nodes"""
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        i = 0

        while i < len(path):
            j = i + 1
            while j < len(path):
                if self._has_direct_connection(path[i], path[j]):
                    j += 1
                else:
                    break
            smoothed.append(path[j - 1])
            i = j - 1

        return smoothed

    def _has_direct_connection(self, node1, node2):
        """Check if two nodes are directly connected in filesystem hierarchy"""
        p1 = Path(node1)
        p2 = Path(node2)

        # Direct parent-child relationship
        if p1 in p2.parents or p2 in p1.parents:
            return True

        # Share common parent within reasonable depth
        common = set(p1.parents) & set(p2.parents)
        if common and min(len(p.parts) for p in common) >= min(len(p1.parts), len(p2.parts)) - 2:
            return True

        return False

    def validate_path(self, path):
        """Verify the path connects start to end"""
        if not path or len(path) < 2:
            return False

        try:
            common_path = os.path.commonpath([path[0], path[-1]])
            return os.path.exists(common_path)
        except ValueError:
            return False