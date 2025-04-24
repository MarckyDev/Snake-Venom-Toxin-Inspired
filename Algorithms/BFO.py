from hmac import new
import random
import os
from os.path import normpath, join, isfile, dirname
import time
import threading
import datetime

from Utils.FileProcessing import FileProcessing
from Utils.PathingUtil import file_limit_reached, timer
from Utils.Metrics import results_in_file



class BacterialForaging:
    def __init__(self, start_dir, target_path, target_file, file_limit=None, run_time_min=0):
        self.start_dir = start_dir
        self.file_limit = file_limit
        self.logged_limits = []
        self.run_time_min = run_time_min
        self.target_path = normpath(target_path)
        self.target_file = target_file
        self.infected_files = 0
        self.infected_nodes = 0
        self.bacteria = []
        self.nutrients = {}
        self.blocked = set()
        self.found_path = None
        self.parent_map = {}  # For path reconstruction
        self.best_path = []
        self.visited_nodes = set()  # Track visited directories
        self.infected_file_set = set()  # Track infected files
        self.search_depth = 0
        self.max_search_depth = 100  # Limit how deep the search goes

        # Timer-related attributes
        self.stop_event = threading.Event()
        self.start_time = time.perf_counter()

    def initialize_bacteria(self, start_dir, num_bacteria=10):
        """Initialize bacteria population at starting directory"""
        start_dir = normpath(start_dir)
        print(f"Initializing bacteria at: {start_dir}")
        print(f"Target file: {join(self.target_path, self.target_file)}")

        self.parent_map[start_dir] = None
        self.visited_nodes.add(start_dir)
        self.infected_nodes += 1

        for _ in range(num_bacteria):
            self.bacteria.append({
                'position': start_dir,
                'health': 100,
                'path': [start_dir],
                'depth': 0
            })

    def evaluate_nutrient(self, path):
        """Calculate fitness of a directory"""
        path = normpath(path)
        if path in self.blocked:
            return -100

        try:
            if path in self.nutrients:
                return self.nutrients[path]

            path_similarity = 0
            target_parts = self.target_path.split(os.sep)
            current_parts = path.split(os.sep)

            common_depth = 0
            for t, c in zip(target_parts, current_parts):
                if t == c:
                    common_depth += 1
                else:
                    break

            path_similarity = common_depth / len(target_parts) * 0.5
            file_count = FileProcessing.count_files_in_directory(path)
            recency = os.path.getmtime(path) if os.path.exists(path) else 0

            nutrient = (file_count * 0.4) + (recency * 0.1) + (path_similarity * 0.5)
            self.nutrients[path] = nutrient
            return nutrient
        except:
            self.blocked.add(path)
            return -100

    def chemotaxis_step(self, bacterium):
        """Move bacterium toward nutrients"""
        current = normpath(bacterium['position'])

        if bacterium['depth'] >= self.max_search_depth:
            bacterium['health'] -= 10
            return False

        if FileProcessing.is_target_in_directory(current, self.target_file):
            print(f"Found target at: {current}")
            self.found_path = current
            self.best_path = bacterium['path'].copy()
            results_in_file(
                self.best_path,
                self.found_path,
                time.perf_counter() - self.start_time,
                self.infected_nodes,
                self.infected_files,
                "Bacterial_Foraging_Optimization",
                self.file_limit
            )

            return True

        neighbors = []
        try:
            for entry in os.listdir(current):
                full_path = join(current, entry)
                if os.path.isdir(full_path):
                    neighbors.append(full_path)

            parent = normpath(dirname(current))
            if parent != current:
                neighbors.append(parent)
        except:
            pass

        graded = []
        for path in neighbors:
            path = normpath(path)
            if path not in self.blocked:
                fitness = self.evaluate_nutrient(path)
                graded.append((path, fitness))

        if not graded:
            self.blocked.add(current)
            return False

        if random.random() < 0.2:
            random.shuffle(graded)
            chosen_path = graded[0][0]
        else:
            total = sum(f for _, f in graded)
            if total <= 0:
                return False

            rand_val = random.uniform(0, total)
            cumulative = 0
            for path, fitness in graded:
                cumulative += fitness
                if rand_val <= cumulative:
                    chosen_path = path
                    break

        bacterium['position'] = chosen_path
        bacterium['path'].append(chosen_path)
        bacterium['depth'] += 1
        self.parent_map[chosen_path] = current

        if chosen_path not in self.visited_nodes:
            self.visited_nodes.add(chosen_path)
            self.infected_nodes += 1

            try:
                for f in os.listdir(chosen_path):
                    file_path = join(chosen_path, f)
                    if isfile(file_path) and file_path not in self.infected_file_set:
                        self.infected_file_set.add(file_path)
                        self.infected_files += 1
            except:
                self.blocked.add(chosen_path)
                return False

        return False

    def reproduction(self):
        """Reproduce healthiest bacteria"""
        self.bacteria.sort(key=lambda x: x['health'], reverse=True)
        top_half = self.bacteria[:max(1, len(self.bacteria) // 2)]
        new_population = []

        for b in top_half:
            # Create two clones with slight variations
            clone1 = {
                'position': b['position'],
                'health': 100,
                'path': list(b['path']),
                'depth': b['depth']
            }

            clone2 = {
                'position': self.get_random_neighbor(b['position']),
                'health': 100,
                'path': list(b['path']),
                'depth': b['depth']
            }

            new_population.extend([clone1, clone2])

        self.bacteria = new_population

    def get_random_neighbor(self, position):
        """Get a random accessible neighbor"""
        position = normpath(position)
        neighbors = []
        try:
            # Add child directories
            for entry in os.listdir(position):
                full_path = join(position, entry)
                if os.path.isdir(full_path) and full_path not in self.blocked:
                    neighbors.append(full_path)

            # Add parent directory if not root
            parent = normpath(dirname(position))
            if parent != position and parent not in self.blocked:
                neighbors.append(parent)
        except:
            pass

        return random.choice(neighbors) if neighbors else position

    def elimination_dispersal(self, p_elim=0.1, start_dir=None):
        """Randomly relocate some bacteria"""
        for i, bacterium in enumerate(self.bacteria):
            if random.random() < p_elim:
                if start_dir:
                    self.bacteria[i]['position'] = normpath(start_dir)
                    self.bacteria[i]['path'] = [normpath(start_dir)]
                    self.bacteria[i]['depth'] = 0
                else:
                    # Randomly select from known accessible paths
                    accessible = [p for p in self.parent_map.keys() if p not in self.blocked]
                    if accessible:
                        new_pos = random.choice(accessible)
                        self.bacteria[i]['position'] = new_pos
                        self.bacteria[i]['path'] = self.reconstruct_path(self.parent_map,new_pos, new_pos)
                        self.bacteria[i]['depth'] = len(self.bacteria[i]['path']) - 1
                self.bacteria[i]['health'] = 100
    def run(self):
        """Main BFO algorithm with integrated timer"""
        self.initialize_bacteria(self.start_dir)
        found = False
        steps = 100_000  # Arbitrary large number of steps for deeper exploration

        # Start timer thread if time limit is set
        timer_thread = None
        if self.run_time_min > 0:
            self.start_time = datetime.now()
            timer_thread = threading.Thread(target=self.timer)
            timer_thread.daemon = True
            timer_thread.start()
        self.parent_map = {self.start_dir: None}
        try:
            if self.stop_event.is_set():
                print("BFO algorithm stopping due to timeout")
                path = self.reconstruct_path(self.parent_map, self.start_dir, self.target_path) # Use the BFO version
                print("im here")

                results_in_file(
                    path,
                    found,
                    time.perf_counter() - self.start_time,
                    self.infected_nodes,
                    self.infected_files,
                    "Bacterial_Foraging_Optimization",
                    self.file_limit
                    )
                return

            while not found and not self.stop_event.is_set() and steps != 0:
                if steps == 1:
                    path = self.reconstruct_path(self.parent_map, self.start_dir, self.target_path)
                    
                    results_in_file(
                        path,
                        found,
                        time.perf_counter() - self.start_time,
                        self.infected_nodes,
                        self.infected_files,
                        "Bacterial_Foraging_Optimization",
                        self.file_limit
                        )
                if self.file_limit:
                    for limit in self.file_limit:
                        print(f"Infected files: {self.infected_files}"
                              f"\n Steps: {steps}"
                              f"\nCurrent File limit: {limit}"
                              f"\nCurrent Logged Limits: {self.logged_limits}")
                        # input("press Enter to continue...")
                        if limit not in self.logged_limits and file_limit_reached(self.infected_files, limit):
                            self.logged_limits.append(limit)
                            path = self.reconstruct_path(self.parent_map, self.start_dir, self.target_path)
                            print("im here")

                            results_in_file(
                                path,
                                found,
                                time.perf_counter() - self.start_time,
                                self.infected_nodes,
                                self.infected_files,
                                "Bacterial_Foraging_Optimization",
                                limit
                            )
                            break

                # Chemotaxis phase
                for bacterium in self.bacteria:
                    if self.chemotaxis_step(bacterium):
                        found = True
                        break

                if found or self.stop_event.is_set():
                    break

                # Update health
                for bacterium in self.bacteria:
                    current_nut = self.evaluate_nutrient(bacterium['position'])
                    if current_nut > 0:
                        bacterium['health'] = min(100, bacterium['health'] + current_nut * 0.1)
                    else:
                        bacterium['health'] -= 5

                    if bacterium['health'] <= 0:
                        self.elimination_dispersal(p_elim=1.0, start_dir=self.start_dir)

                # Reproduction phase
                if steps % 10 == 0:
                    self.reproduction()

                # Elimination and dispersal
                if steps % 50 == 0:
                    self.elimination_dispersal(start_dir=self.start_dir)
                steps -= 1

        finally:
            # Clean up timer thread
            if timer_thread and timer_thread.is_alive():
                self.stop_event.set()
                timer_thread.join()

        # Return results
        if self.best_path:
            path_display = os.path.sep.join(self.best_path)
            path = self.reconstruct_path(self.parent_map, self.start_dir, self.target_path)
            print("Found the best path!")
            results_in_file(
                path,
                found,
                time.perf_counter() - self.start_time,
                self.infected_nodes,
                self.infected_files,
                "Bacterial_Foraging_Optimization",
                self.file_limit
            )

        else:
            path_display = f"Searching... (Depth: {self.search_depth})"

        return [path_display, self.infected_files, self.infected_nodes]

    def _reconstruct_path_generator_bf(self, parent_map, start, end):
        """
        Generator function to reconstruct the path for BFO.
        Traces back from 'end' to 'start' using the 'parent_map'.
        """
        current = end
        while current != start:
            if current not in parent_map:
                raise ValueError("Start or end node not in parent_map.")
            yield current
            current = parent_map[current]
        yield start

    def reconstruct_path(self, parent_map, start, end):
        """
        Reconstructs the path from 'start' to 'end' for BFO using the parent map.
        It uses a generator and returns the path as a list.
        """
        path = list(self._reconstruct_path_generator_bf(parent_map, start, end))
        return path[::-1]