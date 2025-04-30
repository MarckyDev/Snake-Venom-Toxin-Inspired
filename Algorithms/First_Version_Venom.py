import os
from os.path import normpath, abspath
import math
import random
import time
import threading
from datetime import datetime

from Utils.FileProcessing import FileProcessing
from Utils.PathingUtil import reconstruct_path
from Utils.PathingUtil import file_limit_reached,  timer
from Utils.Metrics import results_in_file


class SnakeVenom:
    def __init__(self, starting_path, ending_path, target_file, seed=0, file_limit=None, run_time_min=0):
        self.file_limit = file_limit
        self.run_time_min = run_time_min
        self.logged_limits = []

        self.starting_path = normpath(abspath(starting_path))
        self.ending_path = normpath(abspath(ending_path))
        self.target_file = target_file
        self.target_found = False

        # Dictionary now stores (priority, counter, path)
        self.open_nodes = {}
        self.counter = 0  # Used to maintain insertion order for equal priorities

        self.parent_map = {self.starting_path: 0}
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

    @staticmethod
    def diffusion_coefficient_calculation(visited):
        if visited == 0:
            return 0
        return (visited / 100 + math.log(visited)) * random.uniform(-0.05, 0.05)

    @staticmethod
    def diffusion_flux(diffusion_coefficient, current_node_value, neighbor_node_value, concentration=1):
        displacement = current_node_value - neighbor_node_value
        if displacement == 0:
            return 0
        return -diffusion_coefficient * (concentration / displacement)

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

    def toxin_decision_effect(self):
        if hasattr(self, 'seed'):
            random.seed(self.seed + self.infected_nodes)
        random_num = random.randint(1, 100)

        if random_num <= 40:
            return self.myotoxin()
        if random_num >= 85:
            return self.neurotoxin()
        return "None"

    def svt_a(self):
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
        cost_map = {current_dir: 0}
        estimated_cost_map = {current_dir: 0}

        # Add starting node to open nodes dictionary
        self.open_nodes[current_dir] = (estimated_cost_map[current_dir], self.counter)
        self.counter += 1
        self.parent_map.update({current_dir: current_dir})

        while self.open_nodes:
            # Get node with lowest estimated cost
            current_dir = min(self.open_nodes, key=self.open_nodes.get)
            current_estimated_cost, _ = self.open_nodes.pop(current_dir)

            threading.Thread(target=self.toxin_decision_effect).start()

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
                results_in_file(
                            path,
                            self.target_found,
                            time.perf_counter() - self.start_time,
                            self.infected_nodes,
                            self.infected_files,
                            "First_Version_Venom",
                            self.file_limit
                        )
                return [
                    path,
                    self.target_found,
                    time.perf_counter() - self.start_time,
                    self.infected_nodes,
                    self.infected_files
                ]

            if self.file_limit:
                print(self.file_limit)
                for limit in self.file_limit:
                    print(limit)
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
                            "First_Version_Venom",
                            limit
                        )
                        print("Im done")

                        break

            try:
                if self.target_file in os.listdir(current_dir):
                    print(f"Found target file: {self.target_file}")
                    self.target_found = True

                    path = reconstruct_path(self.parent_map, self.starting_path, current_dir)
                    results_in_file(
                        path,
                        self.target_found,
                        time.perf_counter() - self.start_time,
                        self.infected_nodes,
                        self.infected_files,
                        "First_Version_Venom",
                        self.file_limit
                    )

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
                next_dirs = FileProcessing().get_all_directories_with_file_counts(current_dir)
            except PermissionError:
                print(f"Access denied to {current_dir}; Skipping...")
                continue

            self.hemotoxin(current_dir)

            if next_dirs:
                for directory in next_dirs:
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
                                self.diffusion_flux(self.diffusion_coefficient_calculation(self.infected_nodes),
                                                        cost_map[current_dir],
                                                        FileProcessing().count_files_in_directory(ending_dir))
                                                    )
                    self.infected_nodes += 1

                    if dir_name not in cost_map or new_cost < cost_map[dir_name]:
                        cost_map[dir_name] = new_cost
                        estimated_cost = (new_cost +
                                          self.diffusion_flux(self.diffusion_coefficient_calculation(self.infected_nodes),
                                              cost_map[dir_name],
                                              FileProcessing().count_files_in_directory(ending_dir))
                                          )
                        estimated_cost_map[dir_name] = estimated_cost
                        self.open_nodes[dir_name] = (estimated_cost, self.counter)
                        self.counter += 1

                        # Count infected files
                    try:
                        for file in os.listdir(dir_name):
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
                parent_dir_file_count = FileProcessing().count_files_in_directory(parent_dir)

                self.parent_map[parent_dir] = current_dir
                estimated_cost = parent_dir_file_count
                self.open_nodes[parent_dir] = (estimated_cost, self.counter)
                self.counter += 1
                cost_map[parent_dir] = parent_dir_file_count

        return [
            reconstruct_path(self.parent_map, self.starting_path, current_dir),
            self.infected_files,
            self.infected_nodes,
            self.myo_count,
            self.neuro_count
        ]