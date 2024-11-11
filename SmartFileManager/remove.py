import os
import argparse
import json
from tqdm import tqdm

script_dir = os.path.dirname(os.path.abspath(__file__))

def main(args):

    database = {}
    try:
        with open(os.path.join(script_dir, 'database.json'), 'r') as f:
            database = json.load(f)
    except FileNotFoundError:
        print("Database not found. Creating a new one...")

    if not os.path.exists(args.path):
        print("Path does not exist.")
        return
    
    print("Remove file tracking from database...")
    path = os.path.realpath(args.path).replace('\\', '/')
    database_paths = database.keys()
    for file in tqdm(database_paths):
        if file.startswith(path):
            database.pop(file)

    with open(os.path.join(script_dir, 'database.json'), 'w') as f:
        json.dump(database, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove tracking from database.')
    parser.add_argument('path', type=str, help='Path to the data directory or file to be removed.')
    args = parser.parse_args()
    main(args)


