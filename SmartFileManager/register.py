import os
import argparse
import json
import hashlib
from tqdm import tqdm

from .utils import PreserveAccessTime, getNeighboringFiles

script_dir = os.path.dirname(os.path.abspath(__file__))

def main(args):
    if not os.path.exists(args.path):
        print("Source path does not exist")
        return
    
    database = {}

    if os.path.exists(os.path.join(script_dir, "database.json")):
        with open(os.path.join(script_dir, "database.json"), "r") as f:
            database = json.load(f)
    
    files = []
    if os.path.isfile(args.path):
        files = [args.path.replace("\\", "/")]
    else:
        files = [os.path.realpath(os.path.join(root, file)).replace("\\", "/") for root, dirs, files in os.walk(args.path) for file in files]

    for idx, file_path in enumerate(tqdm(files)):
        modified_time = os.path.getmtime(file_path)
        if file_path in database:
            if modified_time == database[file_path]["modified_time"]:
                continue
            
        database[file_path]["modified_time"] = modified_time
        database[file_path]["created_time"] = os.path.getctime(file_path)

        # Retrieve "human" accessed time by checking the neighboring files, if there are other multiple files with small time difference in accessed time compared to the current, the accessed time is considered as "bot" accessed time.
        # 1. Find all the neighboring files
        if 'neighbour_files' in database[file_path] and len([f for f in database[file_path]['neighbour_files'] if not os.path.exists(f)]) == 0:
            neighbour_files = database[file_path]['neighbour_files']
        else:
            neighbour_files = []
            for neighbor in getNeighboringFiles(file_path):
                if len(neighbour_files) < 10:
                    neighbour_files.append(neighbor)
                else:
                    break
            database[file_path]['neighbour_files'] = neighbour_files

        # 2. Get the differences
        neighbour_accessed_times = [os.path.getatime(f) for f in neighbour_files]
        current_file_accessed_time = os.path.getatime(file_path)
        min_time_diff = min([abs(current_file_accessed_time - t) for t in neighbour_accessed_times])

        # 3. Set the accessed time as the current file accessed time if the minimum difference is greater than 3 seconds
        if min_time_diff is None or min_time_diff >= 3:
            database[file_path]['accessed_time'] = current_file_accessed_time

        with PreserveAccessTime(file_path):
            database[file_path]["hash"] = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()

        if idx % 1000 == 0:
            with open(os.path.join(script_dir, "database.json"), "w") as f:
                json.dump(database, f, indent=4)
    
    with open(os.path.join(script_dir, "database.json"), "w") as f:
        json.dump(database, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Register data to the tracking system')
    parser.add_argument('path', help='Path of the data to be registered')
    args = parser.parse_args()
    main(args)


