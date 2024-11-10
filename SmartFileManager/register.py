import os
import argparse
import json
import hashlib
from tqdm import tqdm
def main(args):
    if not os.path.exists(args.source_path):
        print("Source path does not exist")
        return
    
    database = {"path2hash": {}, "hash2path": {}}

    if os.path.exists("database.json"):
        with open("database.json", "r") as f:
            database = json.load(f)

    files = [os.path.join(root, file) for root, dirs, files in os.walk(args.source_path) for file in files]

    for idx, file_path in enumerate(tqdm(files)):
        modified_time = os.path.getmtime(file_path)
        if file_path in database["path2hash"]:
            # get modified time of the file
            if modified_time == database["path2hash"][file_path]["modified_time"]:
                continue
            else:
                # resolve the conflict here
                ...
        else:
            sha512_hash = None

            #calculate sha512 hash of the file
            with open(file_path, 'rb') as f:
                data = f.read()
                sha512_hash = hashlib.sha512(data).hexdigest()

            database["path2hash"][file_path] = {
                "sha512":sha512_hash,
                "modified_time": modified_time,
            }

            if sha512_hash not in database["hash2path"]:
                database["hash2path"][sha512_hash] = [file_path]
            else:
                database["hash2path"][sha512_hash].append(file_path)

        if idx % 1000 == 0:
            with open("database.json", "w") as f:
                json.dump(database, f, indent=4)
    
    with open("database.json", "w") as f:
        json.dump(database, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Register a source to the system')
    parser.add_argument('--source-path', help='Path of the source to be registered')
    args = parser.parse_args()

    main(args)


