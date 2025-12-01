import os
import json
import argparse
import fnmatch

def find_files(path, pattern, limit):
    matches = []
    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, pattern):
            matches.append(os.path.join(root, filename))
            if limit and len(matches) >= limit:
                return matches
    return matches

def main():
    parser = argparse.ArgumentParser(description="File Finder")
    parser.add_argument("--pattern", required=True, help="Glob pattern")
    parser.add_argument("--path", default=".", help="Root directory to search")
    parser.add_argument("--limit", type=int, help="Max results")
    
    args = parser.parse_args()
    
    files = find_files(args.path, args.pattern, args.limit)
    print(json.dumps({"files": files}, indent=2))

if __name__ == "__main__":
    main()
