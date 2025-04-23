import os
from os.path import normpath
from pathlib import Path
import datetime
import time
import threading
from Utils.FileProcessing import FileProcessing
from Utils.PathingUtil import file_limit_reached, timer
from Utils.Metrics import results_in_file


class EBSAStar:
    def __init__(self, current_dir, ending_path, target_file, file_limit=None, run_time_min=0):
        self.current_dir = current_dir
        self.file_limit = file_limit
        self.logged_limits = []
        self.run_time_min = run_time_min
        self.ending_path = normpath(ending_path)
        self.target_found = False
        self.infected_nodes = 0
        self.infected_files = 0
        self.blocked_directories = set()
        self.processed_files = set()
        self.target_file = target_file
        self.forward_parents = {}
        self.backward_parents = {}
        self.intersection_node = None

        self.stop_event = threading.Event()
        self.start_time = time.perf_counter()

    def _infect_directory(self, dir_path):
        """Accurate file counting with deduplication"""
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
                    if self.file_limit:
                        for limit in self.file_limit:
                            if limit not in self.logged_limits and file_limit_reached(self.infected_files, limit):
                                results_in_file(
                                    None,  # Path might not be found yet
                                    self.target_found,
                                    time.perf_counter() - self.start_time,
                                    self.infected_nodes,
                                    self.infected_files,
                                    "Enhanced_BiDirectional_A_Search",
                                    limit
                                )
                                self.logged_limits.append(limit)

        except Exception as e:
            print(f"Error in {dir_path}: {str(e)}")

    def heuristic(self, current_count, target_count):
        """Improved heuristic considering both file count difference and depth"""
        return abs(current_count - target_count)


    def get_neighbors(self, node):
        """Get all accessible directories with file counts and status"""
        try:
            neighbors = FileProcessing().get_all_directories_with_file_counts(node)
            for neighbor in neighbors:
                neighbor["dir_name"] = normpath(neighbor["dir_name"])
            return neighbors
        except PermissionError:
            print(f"Access denied to {node}. Skipping this directory.")
            return []
        except Exception as e:
            print(f"Error getting neighbors for {node}: {str(e)}")
            return []

    def search(self, node, open_list, close_list, goal, is_forward_search, parents):
        """Enhanced search with parent directory fallback"""
        neighbors = self.get_neighbors(node)

        # Parent directory fallback
        if not neighbors and node != os.path.dirname(node):
            parent_dir = normpath(os.path.dirname(node))
            if parent_dir not in close_list and not any(n[0] == parent_dir for n in open_list):
                parent_g = FileProcessing().count_files_in_directory(node)  # Cost to reach parent
                parent_h = self.heuristic(
                    FileProcessing().count_files_in_directory(parent_dir),
                    FileProcessing().count_files_in_directory(goal)
                )
                parent_f = parent_g + parent_h
                open_list.append((parent_dir, parent_g, parent_h, parent_f))
                parents[parent_dir] = node

            else:
                grandparent_dir = normpath(os.path.dirname(os.path.dirname(node)))
                if grandparent_dir and grandparent_dir not in close_list and not any(n[0] == grandparent_dir for n in open_list):
                    grandparent_g = FileProcessing().count_files_in_directory(parent_dir) # Cost to reach grandparent
                    grandparent_h = self.heuristic(
                        FileProcessing().count_files_in_directory(grandparent_dir),
                        FileProcessing().count_files_in_directory(goal)
                    )
                    grandparent_f = grandparent_g + grandparent_h
                    open_list.append((grandparent_dir, grandparent_g, grandparent_h, grandparent_f))
                    parents[grandparent_dir] = os.path.dirname(node)

        for neighbor in neighbors:
            dir_name = neighbor["dir_name"]
            value = neighbor["value"]
            status = neighbor["status"]

            if dir_name in self.blocked_directories:
                continue

            if dir_name not in close_list and not any(n[0] == dir_name for n in open_list):
                new_g = FileProcessing().count_files_in_directory(node) + 1 # Assuming cost of 1 to move to neighbor
                new_h = self.heuristic(value, FileProcessing().count_files_in_directory(goal))
                new_f = new_g + new_h
                open_list.append((dir_name, new_g, new_h, new_f))
                parents[dir_name] = node

                if status == "vulnerable":
                    self._infect_directory(dir_name)

    def ebs_astar(self):
        """Enhanced Bidirectional A* Search with built-in timeout"""
        current_dir = normpath(self.current_dir)
        path = self._reconstruct_path(self.forward_parents, self.backward_parents, self.intersection_node)
        self.target_found = False
        # Initialize data structures
        start_node = (current_dir, 0,
                      self.heuristic(FileProcessing().count_files_in_directory(current_dir),
                                     FileProcessing().count_files_in_directory(self.ending_path)), 0)
        goal_node = (self.ending_path, 0,
                     self.heuristic(FileProcessing().count_files_in_directory(self.ending_path),
                                    FileProcessing().count_files_in_directory(current_dir)), 0)

        OPEN_LIST_1 = [start_node]
        OPEN_LIST_2 = [goal_node]
        CLOSE_LIST_1 = set()
        CLOSE_LIST_2 = set()
        self.forward_parents = {current_dir: None}
        self.backward_parents = {self.ending_path: None}

        intersection_node = None

        while OPEN_LIST_1 and OPEN_LIST_2:
            # Check if the runtime limit has been reached
            # Start timer thread if time limit is set
            timer_thread = None
            if self.run_time_min > 0:
                self.start_time = datetime.now()
                timer_thread = threading.Thread(target=timer, args=(self.start_time, self.run_time_min, self.stop_event))
                timer_thread.daemon = True
                timer_thread.start()
            
            if self.stop_event.is_set():
                print("Time limit reached. Stopping the process.")
                path = self._reconstruct_path(self.forward_parents, self.backward_parents, self.intersection_node)
                print(f"Path: {path}")
                results_in_file(
                    path,
                    self.target_found,
                    time.perf_counter() - self.start_time,
                    self.infected_nodes,
                    self.infected_files,
                    "Enhanced_BiDirectional_A_Search",
                    self.file_limit
                )
                return
            
            # Check file limit condition
            if self.file_limit:
                for limit in self.file_limit:
                    if limit not in self.logged_limits and file_limit_reached(self.infected_files, limit):
                        results_in_file(
                            path,  # path might be None here if no intersection
                            self.target_found,
                            time.perf_counter() - self.start_time,
                            self.infected_nodes,
                            self.infected_files,
                            "Enhanced_BiDirectional_A_Search",
                            limit
                        )
                        self.logged_limits.append(limit)

            print(f"Infected File: {self.infected_files}")
            print(f"Infected Node: {self.infected_nodes}")
            print(f"Intersection Node: {intersection_node}")

            # Forward search
            if OPEN_LIST_1:
                current_s = min(OPEN_LIST_1, key=lambda x: x[3])
                OPEN_LIST_1.remove(current_s)
                current_s_node = current_s[0]
                CLOSE_LIST_1.add(current_s_node)

                if current_s_node in CLOSE_LIST_2:
                    intersection_node = current_s_node
                    path = self._reconstruct_path(self.forward_parents, self.backward_parents, self.intersection_node)
                    if self.validate_path(path):
                        self.target_found = True
                        # Check file limit after finding a valid path
                        if self.file_limit:
                            for limit in self.file_limit:
                                if limit not in self.logged_limits and file_limit_reached(self.infected_files, limit):
                                    results_in_file(
                                        path,
                                        self.target_found,
                                        time.perf_counter() - self.start_time,
                                        self.infected_nodes,
                                        self.infected_files,
                                        "Enhanced_BiDirectional_A_Search",
                                        limit
                                    )
                                    self.logged_limits.append(limit)
                        break  # Exit after finding a path

                self.search(current_s_node, OPEN_LIST_1, CLOSE_LIST_1, self.ending_path, True, self.forward_parents)

            # Backward search
            if OPEN_LIST_2:
                current_e = min(OPEN_LIST_2, key=lambda x: x[3])
                OPEN_LIST_2.remove(current_e)
                current_e_node = current_e[0]
                CLOSE_LIST_2.add(current_e_node)

                if current_e_node in CLOSE_LIST_1:
                    intersection_node = current_e_node
                    path = self._reconstruct_path(self.forward_parents, self.backward_parents, intersection_node)
                    if self.validate_path(path):
                        self.target_found = True
                        search_successful = True
                        break  # Exit the while loop upon finding a path

                self.search(current_e_node, OPEN_LIST_2, CLOSE_LIST_2, current_dir, False, self.backward_parents)

        # Log results after the search loop finishes
        results_in_file(
            path,
            self.target_found,
            time.perf_counter() - self.start_time,
            self.infected_nodes,
            self.infected_files,
            "Enhanced_BiDirectional_A_Search",
            self.file_limit
        )
        return [path, self.infected_files, self.infected_nodes]


    def has_direct_connection(self, node1, node2):
        """Check if two nodes are directly connected (parent-child or share grandparent)"""
        p1 = Path(node1)
        p2 = Path(node2)

        # Direct parent-child relationship
        if p1 in p2.parents or p2 in p1.parents:
            return True

        # Share common parent within 2 levels
        common = set(p1.parents) & set(p2.parents)
        if common and min(len(p.parts) for p in common) >= min(len(p1.parts), len(p2.parts)) - 2:
            return True

        return False

    def smoothing(self, path):
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        i = 0

        while i < len(path):
            j = i + 1
            while j < len(path):
                if self.has_direct_connection(path[i], path[j]):
                    j += 1
                else:
                    break
            smoothed.append(path[j - 1])
            i = j - 1

        return smoothed

    def _reconstruct_path(self, forward_parents, backward_parents, intersection):
        """Reconstruct the complete path from both directions and return it as a list."""
        # Reconstruct forward path
        current = intersection
        forward_path = []
        while current is not None:
            forward_path.append(current)
            current = forward_parents.get(current)
        forward_path.reverse()

        # Reconstruct backward path
        backward_path = []
        current = backward_parents.get(intersection)
        while current is not None:
            backward_path.append(current)
            current = backward_parents.get(current)

        # Combine forward and backward paths
        full_path = forward_path + backward_path
        return full_path

    def validate_path(self, path):
        """Verify the path connects start to end"""
        if not path or len(path) < 2:
            return False

        try:
            common_path = os.path.commonpath([path[0], path[-1]])
            return os.path.exists(common_path)
        except ValueError:
            return False

    def check_duplicates(self):
        from collections import Counter
        dupes = Counter(self.processed_files)
        print(f"Total files: {len(self.processed_files)}")
        print(f"Unique files: {len(dupes)}")
        print(f"Duplicates: {sum(v - 1 for v in dupes.values() if v > 1)}")