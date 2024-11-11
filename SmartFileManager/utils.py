import os
from typing import List

import hermetrics

# Adapted from ChatGPT
class PreserveAccessTime:
    def __init__(self, file_path: str | List[str], override_atime: float | List[float] = None):
        if isinstance(file_path, str):
            self.file_paths = [file_path]
        else:
            self.file_paths = file_path

        self.original_atimes = override_atime
    
    def __enter__(self):
        # Store the original access and modification times
        if self.original_atimes is None:
            self.original_atimes = [os.path.getatime(file_path) for file_path in self.file_paths if os.path.exists(file_path)]

    def __exit__(self, exc_type, exc_val, exc_tb):
        for index, file in enumerate(self.file_paths):
            if os.path.exists(file):
                atime = self.original_atimes[index] if isinstance(self.original_atimes, list) else self.original_atimes
                os.utime(file, (atime, os.path.getmtime(file)))

def getNeighboringFiles(file_path: str):
    """
    Returns a list of neighboring files to the given file path.
    """
    file_dir = os.path.realpath(file_path).replace("\\", "/")
    searched_branch = "???"
    metric = hermetrics.DamerauLevenshtein()
    try:
        while True:
            file_dir = os.path.dirname(file_dir)
            for root, dirs, files in os.walk(file_dir):
                if not root.startswith(searched_branch):
                    # sort by edit distance
                    files = sorted(files, key=lambda x: metric.distance(source=os.path.basename(file_path).split(".")[0], target=x.split(".")[0]))
                    for file in files:
                        if file != os.path.basename(file_path):
                            yield os.path.join(root, file)
            searched_branch = file_dir
    except Exception as e:
        print(e)
    return
