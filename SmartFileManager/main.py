

from .optimize import main as optimize_main
from .register import main as register_main
from .remove import main as remove_main
import argparse

def main():
    parser = argparse.ArgumentParser(prog="SmartFileManager", description='Smart File Manager CLI')
    # there are optimize, register, and remove commands
    subparsers = parser.add_subparsers(dest="command", help='command to execute')

    register_parser = subparsers.add_parser('register', help='Register a directory or file to the tracking system')
    register_parser.add_argument('path', type=str, help='path to the directory or file to be registered')

    remove_parser = subparsers.add_parser('remove', help='Remove a directory or file from the tracking system')
    remove_parser.add_argument('path', type=str, help='path to the directory or file to be removed')

    optimize_parser = subparsers.add_parser('optimize', help='Optimize the tracking system')
    
    args = parser.parse_args()

    if args.command == 'optimize':
        optimize_main(args)
    elif args.command =='register':
        register_main(args)
    elif args.command =='remove':
        remove_main(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
    