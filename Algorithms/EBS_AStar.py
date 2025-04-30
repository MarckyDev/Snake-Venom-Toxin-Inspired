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
        print(f"Initializing EBSAStar with: current_dir={current_dir}, ending_path={ending_path}, target_file={target_file}, file_limit={file_limit}, run_time_min={run_time_min}")
        self.current_dir = current_dir
        self.file_limit = file_limit
        self.logged_limits = []
        self.run_time_min = run_time_min
        self.ending_path = normpath(ending_path)
        self.target_found = False
        self.infected_nodes = 0
        self.infected_files = 0
        self.processed_files = set()
        self.target_file = target_file
        self.forward_parents = {}
        self.backward_parents = {}
        self.intersection_node = None

        self.stop_event = threading.Event()
        self.start_time = time.perf_counter()
        print("EBSAStar initialization complete")

    def _infect_directory(self, dir_path, close_list):
        """Accurate file counting with deduplication"""
        try:
            dir_path = normpath(dir_path)
            print(f"Attempting to infect directory: {dir_path}")
            
            if dir_path in close_list:
                print(f"Directory {dir_path} already in close list, skipping")
                return

            close_list.add(dir_path)
            self.infected_nodes += 1
            print(f"Added {dir_path} to close list. Total infected nodes: {self.infected_nodes}")

            for f in os.listdir(dir_path):
                file_path = os.path.join(dir_path, f)
                if os.path.isfile(file_path) and file_path not in self.processed_files:
                    self.processed_files.add(file_path)
                    self.infected_files += 1
                    print(f"Processed file {file_path}. Total files: {self.infected_files}")
                    
                    if self.file_limit:
                        for limit in self.file_limit:
                            if limit not in self.logged_limits and file_limit_reached(self.infected_files, limit):
                                print(f"File limit {limit} reached at {self.infected_files} files")
                                results_in_file(
                                    None,
                                    self.target_found,
                                    time.perf_counter() - self.start_time,
                                    self.infected_nodes,
                                    self.infected_files,
                                    "Enhanced_BiDirectional_A_Search",
                                    limit
                                )
                                self.logged_limits.append(limit)

        except Exception as e:
            print(f"ERROR in _infect_directory for {dir_path}: {str(e)}")

    def heuristic(self, current_count, target_count):
        """Improved heuristic considering both file count difference and depth"""
        h = abs(current_count - target_count)
        print(f"Calculating heuristic: current={current_count}, target={target_count}, result={h}")
        return h

    def get_neighbors(self, node):
        """Get all accessible directories with file counts and status"""
        try:
            print(f"Getting neighbors for node: {node}")
            neighbors = FileProcessing().get_all_directories_with_file_counts(node)
            for neighbor in neighbors:
                neighbor["dir_name"] = normpath(neighbor["dir_name"])
            print(f"Found {len(neighbors)} neighbors for {node}")
            return neighbors
        except PermissionError:
            print(f"ACCESS DENIED to {node}. Skipping this directory.")
            return []
        except Exception as e:
            print(f"ERROR getting neighbors for {node}: {str(e)}")
            return []

    def search(self, node, open_list, close_list, goal, is_forward_search, parents):
        """Enhanced search with parent and grandparent directory fallback"""
        print(f"Searching from node: {node} (forward={is_forward_search})")
        neighbors = self.get_neighbors(node)

        # Enhanced parent/grandparent directory fallback
        if not neighbors:
            print(f"No neighbors found for {node}, attempting parent/grandparent fallback")
            parent_dir = normpath(os.path.dirname(node))
            
            # First try parent directory
            if parent_dir and parent_dir != node:
                if parent_dir not in close_list and not any(n[0] == parent_dir for n in open_list):
                    parent_g = FileProcessing().count_files_in_directory(node)
                    parent_h = self.heuristic(
                        FileProcessing().count_files_in_directory(parent_dir),
                        FileProcessing().count_files_in_directory(goal)
                    )
                    parent_f = parent_g + parent_h
                    print(f"Adding parent to open list: {parent_dir}, g={parent_g}, h={parent_h}, f={parent_f}")
                    open_list.append((parent_dir, parent_g, parent_h, parent_f))
                    parents[parent_dir] = node
                    print(f"Set parent relationship: {parent_dir} -> {node}")
                else:
                    print(f"Parent {parent_dir} already in close list or open list, trying grandparent")
                    # If parent is already processed, try grandparent
                    grandparent_dir = normpath(os.path.dirname(parent_dir))
                    if grandparent_dir and grandparent_dir != parent_dir:
                        if grandparent_dir not in close_list and not any(n[0] == grandparent_dir for n in open_list):
                            grandparent_g = FileProcessing().count_files_in_directory(parent_dir)
                            grandparent_h = self.heuristic(
                                FileProcessing().count_files_in_directory(grandparent_dir),
                                FileProcessing().count_files_in_directory(goal)
                            )
                            grandparent_f = grandparent_g + grandparent_h
                            print(f"Adding grandparent to open list: {grandparent_dir}, g={grandparent_g}, h={grandparent_h}, f={grandparent_f}")
                            open_list.append((grandparent_dir, grandparent_g, grandparent_h, grandparent_f))
                            parents[grandparent_dir] = parent_dir
                            print(f"Set grandparent relationship: {grandparent_dir} -> {parent_dir}")
                        else:
                            print(f"Grandparent {grandparent_dir} already in close list or open list")
                    else:
                        print(f"Already at root directory {parent_dir}, cannot go higher")
            else:
                print(f"Already at root directory {node}, cannot go higher")

        # Process regular neighbors if any exist
        for neighbor in neighbors:
            dir_name = neighbor["dir_name"]
            value = neighbor["value"]
            status = neighbor["status"]
            print(f"Processing neighbor: {dir_name}, value={value}, status={status}")

            if dir_name in close_list:
                print(f"Neighbor {dir_name} already in close list, skipping")
                continue

            if dir_name not in close_list and not any(n[0] == dir_name for n in open_list):
                new_g = FileProcessing().count_files_in_directory(node) + 1
                new_h = self.heuristic(value, FileProcessing().count_files_in_directory(goal))
                new_f = new_g + new_h
                print(f"Adding new neighbor to open list: {dir_name}, g={new_g}, h={new_h}, f={new_f}")
                open_list.append((dir_name, new_g, new_h, new_f))
                parents[dir_name] = node

                if status == "vulnerable":
                    print(f"Neighbor {dir_name} is vulnerable, infecting...")
                    self._infect_directory(dir_name, close_list)

    def ebs_astar(self):
        """Enhanced Bidirectional A* Search with built-in timeout"""
        print("Starting EBS A* search")
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

        print(f"Start node: {start_node}")
        print(f"Goal node: {goal_node}")

        OPEN_LIST_1 = [start_node]
        OPEN_LIST_2 = [goal_node]
        CLOSE_LIST_1 = set()
        CLOSE_LIST_2 = set()
        self.forward_parents = {current_dir: None}
        self.backward_parents = {self.ending_path: None}

        intersection_node = None

        # Start timer thread if time limit is set
        timer_thread = None
        if self.run_time_min > 0:
            print(f"Setting timer for {self.run_time_min} minutes")
            self.start_time = time.perf_counter()
            timer_thread = threading.Thread(target=timer, args=(self.start_time, self.run_time_min, self.stop_event))
            timer_thread.daemon = True
            timer_thread.start()

        while OPEN_LIST_1 and OPEN_LIST_2:
            print("\n--- New iteration ---")
            print(f"OPEN_LIST_1 size: {len(OPEN_LIST_1)}")
            print(f"OPEN_LIST_2 size: {len(OPEN_LIST_2)}")
            print(f"CLOSE_LIST_1 size: {len(CLOSE_LIST_1)}")
            print(f"CLOSE_LIST_2 size: {len(CLOSE_LIST_2)}")
            
            # Check if the runtime limit has been reached
            if self.stop_event.is_set():
                print("TIME LIMIT REACHED. Stopping the process.")
                path = self._reconstruct_path(self.forward_parents, self.backward_parents, self.intersection_node)
                print(f"Current path: {path}")
                results_in_file(
                    path,
                    self.target_found,
                    time.perf_counter() - self.start_time,
                    self.infected_nodes,
                    self.infected_files,
                    "Enhanced_BiDirectional_A_Search",
                    self.file_limit
                )
                return [
                    path,
                    self.target_found,
                    time.perf_counter() - self.start_time,
                    self.infected_nodes,
                    self.infected_files
                ]
            
            # Check file limit condition
            if self.file_limit:
                for limit in self.file_limit:
                    if limit not in self.logged_limits and file_limit_reached(self.infected_files, limit):
                        print(f"FILE LIMIT {limit} REACHED at {self.infected_files} files")
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

            print(f"Infected Files: {self.infected_files}")
            print(f"Infected Nodes: {self.infected_nodes}")
            print(f"Intersection Node: {intersection_node}")

            # Forward search
            if OPEN_LIST_1:
                current_s = min(OPEN_LIST_1, key=lambda x: x[3])
                OPEN_LIST_1.remove(current_s)
                current_s_node = current_s[0]
                CLOSE_LIST_1.add(current_s_node)
                print(f"Forward search processing: {current_s_node}")

                if current_s_node in CLOSE_LIST_2:
                    intersection_node = current_s_node
                    self.intersection_node = intersection_node
                    print(f"INTERSECTION FOUND at {intersection_node}")
                    path = self._reconstruct_path(self.forward_parents, self.backward_parents, intersection_node)
                    if self.validate_path(path):
                        self.target_found = True
                        print(f"VALID PATH FOUND: {path}")
                        if self.file_limit:
                            for limit in self.file_limit:
                                if limit not in self.logged_limits and file_limit_reached(self.infected_files, limit):
                                    print(f"File limit {limit} reached after path found")
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
                        break

                self.search(current_s_node, OPEN_LIST_1, CLOSE_LIST_1, self.ending_path, True, self.forward_parents)

            # Backward search
            if OPEN_LIST_2:
                current_e = min(OPEN_LIST_2, key=lambda x: x[3])
                OPEN_LIST_2.remove(current_e)
                current_e_node = current_e[0]
                CLOSE_LIST_2.add(current_e_node)
                print(f"Backward search processing: {current_e_node}")

                if current_e_node in CLOSE_LIST_1:
                    intersection_node = current_e_node
                    self.intersection_node = intersection_node
                    print(f"INTERSECTION FOUND at {intersection_node}")
                    path = self._reconstruct_path(self.forward_parents, self.backward_parents, intersection_node)
                    if self.validate_path(path):
                        self.target_found = True
                        print(f"VALID PATH FOUND: {path}")
                        break

                self.search(current_e_node, OPEN_LIST_2, CLOSE_LIST_2, current_dir, False, self.backward_parents)

        # Log results after the search loop finishes
        print("Search loop ended")
        print(f"Final path: {path}")
        print(f"Target found: {self.target_found}")
        print(f"Total infected files: {self.infected_files}")
        print(f"Total infected nodes: {self.infected_nodes}")
        
        results_in_file(
            path,
            self.target_found,
            time.perf_counter() - self.start_time,
            self.infected_nodes,
            self.infected_files,
            "Enhanced_BiDirectional_A_Search",
            self.file_limit
        )
        return [
                path,
                self.target_found,
                time.perf_counter() - self.start_time,
                self.infected_nodes,
                self.infected_files
                ]

    def has_direct_connection(self, node1, node2):
        """Check if two nodes are directly connected (parent-child or share grandparent)"""
        print(f"Checking direct connection between {node1} and {node2}")
        p1 = Path(node1)
        p2 = Path(node2)

        # Direct parent-child relationship
        if p1 in p2.parents or p2 in p1.parents:
            print("Direct parent-child relationship found")
            return True

        # Share common parent within 2 levels
        common = set(p1.parents) & set(p2.parents)
        if common and min(len(p.parts) for p in common) >= min(len(p1.parts), len(p2.parts)) - 2:
            print(f"Common parent found within 2 levels: {common}")
            return True

        print("No direct connection found")
        return False

    def smoothing(self, path):
        print(f"Smoothing path: {path}")
        if len(path) <= 2:
            print("Path too short, no smoothing needed")
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

        print(f"Smoothed path: {smoothed}")
        return smoothed

    def _reconstruct_path(self, forward_parents, backward_parents, intersection):
        """Reconstruct the complete path from both directions and return it as a list."""
        print(f"Reconstructing path with intersection at {intersection}")
        
        if intersection is None:
            print("No intersection node, returning empty path")
            return []
            
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
        print(f"Reconstructed full path: {full_path}")
        return full_path

    def validate_path(self, path):
        """Verify the path connects start to end"""
        print(f"Validating path: {path}")
        if not path or len(path) < 2:
            print("Path too short or empty")
            return False

        try:
            common_path = os.path.commonpath([path[0], path[-1]])
            exists = os.path.exists(common_path)
            print(f"Common path: {common_path}, exists: {exists}")
            return exists
        except ValueError as e:
            print(f"Path validation error: {str(e)}")
            return False

    def check_duplicates(self):
        from collections import Counter
        print("Checking for duplicate files")
        dupes = Counter(self.processed_files)
        print(f"Total files: {len(self.processed_files)}")
        print(f"Unique files: {len(dupes)}")
        print(f"Duplicates: {sum(v - 1 for v in dupes.values() if v > 1)}")