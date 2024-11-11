import os
import argparse
import json
import hashlib
import shutil
import time
from tqdm import tqdm

from .utils import PreserveAccessTime, getNeighboringFiles

script_dir = os.path.dirname(os.path.abspath(__file__))

def main(args):
    database = {} if not os.path.exists(os.path.join(script_dir, 'database.json')) else json.load(open(os.path.join(script_dir, 'database.json'), 'r'))

    config = {}
    if not os.path.exists(os.path.join(script_dir, "config.json")):
        storage_path = input("Initialize the storage, please enter the storage path: ")
        config = {
            'storage_path': storage_path,
            'exclude': []
        }
        json.dump(config, open(os.path.join(script_dir, "config.json"), "w"), indent=4)
    else:
        config = json.load(open(os.path.join(script_dir, "config.json"), "r"))

    try:
        os.makedirs(config['storage_path'], exist_ok=True)
    except:
        print("Failed to create storage path, please check the path and try again.")
        return
    
    print("Update database...")
    for file_path, metadata in tqdm(database.items()):
        if not os.path.exists(file_path):
            database.pop(file_path)
            continue

        # we only care about accessed time triggered by human not "bot" touches, more details refer to register.py: "Retrieve "human" accessed time by checking the neighboring files"
        if 'neighbour_files' in metadata and len([f for f in metadata['neighbour_files'] if not os.path.exists(f)]) == 0:
            neighbour_files = metadata['neighbour_files']
        else:
            neighbour_files = []
            for neighbor in getNeighboringFiles(file_path):
                if len(neighbour_files) < 10:
                    neighbour_files.append(neighbor)
                else:
                    break
            metadata['neighbour_files'] = neighbour_files
        neighbour_accessed_times = [os.path.getatime(f) for f in neighbour_files]
        current_file_accessed_time = os.path.getatime(file_path)
        min_time_diff = min([abs(current_file_accessed_time - t) for t in neighbour_accessed_times])
        if min_time_diff is None or min_time_diff >= 3:
            database[file_path]['accessed_time'] = current_file_accessed_time
    
        if os.path.getmtime(file_path) > metadata['modified_time']:
            with PreserveAccessTime(file_path):
                database[file_path]['hash'] = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()
            database[file_path]['modified_time'] = os.path.getmtime(file_path)

    with open(os.path.join(script_dir, 'database.json'), 'w') as f:
        json.dump(database, f, indent=4)

    print("Evicting long-time-inactive files...")
    for file_path, metadata in tqdm(database.items()):
        if not os.path.exists(file_path):
            continue
        
        accessed_time = metadata.get('accessed_time', None)
        with PreserveAccessTime(file_path, accessed_time):
            if os.path.islink(file_path) and accessed_time and accessed_time >= time.time() - 60*60*24*7: # if the file is a link and it's accessed within 7 days, restore it to its original location
                    storage_path = os.path.realpath(file_path)
                    os.remove(file_path)
                    shutil.copyfile(storage_path, file_path)
                    os.remove(storage_path)
            elif accessed_time and accessed_time < time.time() - 60*60*24*7: # if the last access is 1 week from now, make a copy of the file and store it in a new location
                    new_file_path = os.path.realpath(os.path.join(config['storage_path'], file_path.replace(":","")))
                    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                    shutil.copyfile(file_path, new_file_path)
                    os.remove(file_path)

                    os.symlink(new_file_path, file_path)
    print("Done.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Optimize the storage')
    args = parser.parse_args()
    main(args)


