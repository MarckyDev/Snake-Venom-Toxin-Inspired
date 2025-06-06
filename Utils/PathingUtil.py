import time
from os.path import normpath

'''
def reconstruct_path(parent_map, start, end):
    """Reconstruct the path from start to end using the parent map."""
    start = normpath(start)
    end = normpath(end)
    print(f"Start Path: {start}")
    print(f"End Path: {end}")
    if start == end:
        return [start]

    if start not in parent_map or end not in parent_map:
        print(f"Start {start} and End {end} \n Parent Map: {parent_map}")
        raise ValueError("Start or end node not found in parent_map.")

    path = [end]
    print(f"Current: {path}")
    while path[-1] != start:

        try:
            path.append(parent_map[path[-1]])
        except KeyError as e:
            raise KeyError(f"Node {path[-1]} not found in parent_map. Path reconstruction failed.") from e

    return path[::-1]
'''

def reconstruct_path(parent_map, start, end):
    """Reconstruct path as a list, but memory-efficient for long paths."""
    path = list(_reconstruct_path_generator(parent_map, start, end))
    return path

def _reconstruct_path_generator(parent_map, start, end):
    """Helper generator for path reconstruction."""
    start = normpath(start)
    end = normpath(end)
    if start == end:
        yield start
        return
    if start not in parent_map or end not in parent_map:
        raise ValueError("Start or end node not in parent_map.")
    current = end
    while current != start:
        yield current
        current = parent_map[current]
    yield start


def timer(start_time, max_run_time_min, stop_event):
    while not stop_event.is_set():
        elapsed = time.perf_counter() - start_time
        if elapsed >= max_run_time_min * 60:
            stop_event.set()
            print(f"Time limit of {max_run_time_min} minutes reached. Stopping...")
            break
        time.sleep(1)  # Check every second to reduce CPU usage

def file_limit_reached(infected_files, file_limit) -> bool:
    return infected_files >= file_limit