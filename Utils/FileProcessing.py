import os
from os.path import normpath, join, isfile
from functools import lru_cache

class FileProcessing:
    def __init__(self):
        pass

    def get_all_directories_with_file_counts(self, base_path):
        """Retrieve all directories in the base path along with their file counts."""
        base_path = normpath(base_path)
        try:
            directories = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        except PermissionError:
            print(f"Access denied to {base_path}. Skipping this directory.")
            return []

        if not directories:
            return []

        directory_info = []
        for directory in directories:
            dir_path = os.path.join(base_path, directory)
            try:
                file_count = self.count_files_in_directory(dir_path)
                directory_info.append({"dir_name": dir_path, "value": file_count, "status": "vulnerable"})
            except PermissionError:
                print(f"Access denied to {dir_path}. Skipping this directory.")
                continue

        return directory_info



    @staticmethod
    @lru_cache(maxsize=None)
    def count_files_in_directory(directory):
        directory = normpath(directory)
        return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])

    @staticmethod
    def get_next_directory(directory):
        """Retrieve the next directory from the given directory."""
        directory = normpath(directory)
        return next(os.walk(directory))[1]

    @staticmethod
    def is_target_in_directory(directory, target_file):
        try:
            target_path = join(directory, target_file)
            return isfile(target_path)
        except:
            return False

