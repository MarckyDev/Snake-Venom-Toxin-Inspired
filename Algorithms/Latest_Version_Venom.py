import heapq
import os
from os.path import normpath, abspath
from datetime import datetime
import random
import time
from heapq import heapify
import threading

from Utils.FileProcessing import FileProcessing
from Utils.PathingUtil import reconstruct_path, file_limit_reached, timer
from Utils.Metrics import results_in_file


class VIPER_Mk_II:
    def __init__(self, starting_path, ending_path, target_file, seed=0, file_limit=None, run_time_min=0):
        self.file_limit = file_limit
        self.run_time_min = run_time_min
        self.logged_limits = []


        self.starting_path = normpath(abspath(starting_path))
        self.ending_path = normpath(abspath(ending_path))
        self.target_file = target_file
        self.target_found = False

        # Heap now stores tuples of (priority, counter, path)
        self.open_nodes = []
        heapify(self.open_nodes)
        self.counter = 0  # Used to maintain insertion order for equal priorities

        self.parent_map = {self.starting_path: self.starting_path}
        self.blocked_directories = set()

        self.locked_files = set()
        self.bypassed_files = set()

        self.infected_nodes = 0
        self.infected_files = 0
        self.myo_count = 0
        self.neuro_count = 0


        self.stop_event = threading.Event()
        self.start_time = time.perf_counter()

        self.seed = seed if seed != 0 or seed is not None else int(time.time() * 1000)
        random.seed(self.seed)
        print(f"Initialized randomizer with seed: {self.seed}")

        self.concentration = 100  # starts as very pure and degrades over time

    def diffusion_flux(self, current_node_value, neighbor_node_value):
        diffusion_coefficient = 1 * random.uniform(0.01, 0.02)
        concentration = self.concentration - self.start_time  # simulates degradation
        displacement = current_node_value - neighbor_node_value

        if displacement == 0:
            return 0

        if concentration <= 0:
            concentration = 1
        return diffusion_coefficient * (concentration / displacement)

    def myotoxin(self):  # loss of control
        self.myo_count += 1
        return "myotoxin"

    def neurotoxin(self):  # loss of nerve function
        self.neuro_count += 1
        return "neurotoxin"

    def hemotoxin(self, current_directory):
        current_directory = normpath(current_directory)
        for f in os.listdir(current_directory):
            file_path = os.path.join(current_directory, f)
            if os.path.isdir(file_path):
                pass

    def toxin_effect(self, current_directory):
        current_directory = normpath(current_directory)
        mode = self.toxin_decision_effect()

        for file in os.listdir(current_directory):
            file_path = os.path.join(current_directory, file)
            if os.path.isfile(file_path):
                if mode == "myotoxin":
                    self.bypassed_files.add(file_path)
                if mode == "neurotoxin":
                    self.locked_files.add(file_path)

    def toxin_decision_effect(self):
        if hasattr(self, 'seed'):
            random.seed(self.seed + self.infected_nodes)
        random_num = random.randint(1, 100)

        if random_num <= 5:
            return self.myotoxin()
        if random_num >= 95:
            return self.neurotoxin()
        return "None"

    def mk_ii(self):
        """
        Returns:
        - Path
        - Infected Nodes
        - Infected Files
        - Myotoxin Activation
        - Neurotoxin Activation
        """
        current_dir = self.starting_path
        ending_dir = self.ending_path

        # Initialize cost maps
        cost_map = {current_dir: self.diffusion_flux(
            FileProcessing().count_files_in_directory(os.path.dirname(current_dir)), # O(Directory Size)
            FileProcessing().count_files_in_directory(ending_dir))} # O(Directory Size)
        estimated_cost_map = {current_dir: 0} # O(1)

        # Push starting node to heap
        heapq.heappush(self.open_nodes, (estimated_cost_map[current_dir], self.counter, current_dir)) # O(log n)
        self.counter += 1
        self.parent_map.update({current_dir: current_dir}) # O(1)

        while self.open_nodes:
            # Get node with lowest estimated cost
            current_estimated_cost, _, current_dir = heapq.heappop(self.open_nodes) # O(log n)
            threading.Thread(target=self.toxin_decision_effect).start() # O(1)

            print(f"Infected nodes:{self.infected_nodes}\n"
                  f"Infected files:{self.infected_files}\n")

            # Start timer thread if time limit is set
            timer_thread = None
            if self.run_time_min > 0:
                timer_thread = threading.Thread(target=timer, args=(self.start_time, self.run_time_min, self.stop_event))
                timer_thread.daemon = True
                timer_thread.start()
            
            if self.stop_event.is_set():
                print("Time limit reached. Stopping the process.")
                path = reconstruct_path(self.parent_map, self.starting_path, current_dir)
                print(f"Path: {path}")
                results_in_file(
                    path,
                    self.target_found,
                    time.perf_counter() - self.start_time,
                    self.infected_nodes,
                    self.infected_files,
                    "Snake_Venom_Latest_Version",
                    self.file_limit
                )
                return [
                    path,
                    self.target_found,
                    time.perf_counter() - self.start_time,
                    self.infected_nodes,
                    self.infected_files
                ]

            if self.file_limit is not None:
                for limit in self.file_limit:
                    if limit not in self.logged_limits and file_limit_reached(self.infected_files, limit):
                        self.logged_limits.append(limit)
                        print(f"Logged Limits: {self.logged_limits}\n"
                              f"I'm Here Processing")
                        path = reconstruct_path(self.parent_map, self.starting_path, current_dir)
                        print(f"Path: {path}")
                        results_in_file(
                            path,
                            self.target_found,
                            time.perf_counter() - self.start_time,
                            self.infected_nodes,
                            self.infected_files,
                            "Snake_Venom_Latest_Version",
                            limit
                        )
                        print("I'm done")

                        break

            try:
                if self.target_file in os.listdir(current_dir): # O(Directory Size)
                    print(f"Found target file: {self.target_file}")
                    self.target_found = True

                    path = reconstruct_path(self.parent_map, self.starting_path, current_dir) # O(n)
                    results_in_file(
                        path,
                        self.target_found,
                        time.perf_counter() - self.start_time,
                        self.infected_nodes,
                        self.infected_files,
                        "Snake_Venom_Latest_Version",
                        self.file_limit
                    ) # O(1)

                    return [
                        reconstruct_path(self.parent_map, self.starting_path, current_dir),
                        self.infected_files,
                        self.infected_nodes,
                        self.myo_count,
                        self.neuro_count
                    ]
            except PermissionError:
                print(f"Access denied to {current_dir}; Skipping...")
                continue

            # Explore subdirectories
            try:
                next_dirs = FileProcessing().get_all_directories_with_file_counts(current_dir) # O(Directory Size)
            except PermissionError:
                print(f"Access denied to {current_dir}; Skipping...")
                continue

            self.hemotoxin(current_dir) # O(Directory Size)

            if next_dirs: 
                for directory in next_dirs: # O(Directory Size)
                    dir_name = normpath(directory["dir_name"])
                    value = directory["value"]
                    status = directory["status"]

                    if dir_name in self.blocked_directories:
                        print(f"Directory {dir_name} is blocked. Moving to next directory...")
                        continue

                    if status == "vulnerable":
                        directory["status"] = "infected"
                        self.blocked_directories.add(current_dir)

                    self.parent_map[dir_name] = current_dir
                    new_cost = (cost_map[current_dir] +
                                self.diffusion_flux(
                                    cost_map[current_dir],
                                    FileProcessing().count_files_in_directory(ending_dir)) # O(Directory Size)
                                )
                    self.infected_nodes += 1

                    if dir_name not in cost_map or new_cost < cost_map[dir_name]: 
                        cost_map[dir_name] = new_cost
                        estimated_cost = (new_cost +
                                          self.diffusion_flux(
                                              cost_map[dir_name],
                                              FileProcessing().count_files_in_directory(ending_dir)) # O(Directory Size)
                                          )
                        estimated_cost_map[dir_name] = estimated_cost
                        heapq.heappush(self.open_nodes, (estimated_cost, self.counter, dir_name)) # O(log n)
                        self.counter += 1

                        # Count infected files
                    try:
                        for file in os.listdir(dir_name): # O(Directory Size)
                            file_path = os.path.join(dir_name, file)
                            if os.path.isfile(file_path):
                                self.infected_files += 1
                    except PermissionError:
                        print(f"Access denied to {dir_name}; Skipping...")
                        continue

            # Move to parent directory
            parent_dir = normpath(os.path.dirname(current_dir))
            if parent_dir != current_dir and parent_dir not in self.blocked_directories:
                print(f"No more Subdirectories, moving up to {parent_dir}")
                parent_dir_file_count = FileProcessing().count_files_in_directory(parent_dir) # O(Directory Size)

                self.parent_map[parent_dir] = current_dir
                estimated_cost = parent_dir_file_count
                heapq.heappush(self.open_nodes, (estimated_cost, self.counter, parent_dir)) # O(log n)
                self.counter += 1
                cost_map[parent_dir] = parent_dir_file_count

        return [
            reconstruct_path(self.parent_map, self.starting_path, current_dir),
            self.infected_files,
            self.infected_nodes,
            self.myo_count,
            self.neuro_count
        ]