import json
import subprocess
import argparse

def get_git_status():
    try:
        # Check if git exists
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        
        # Get status
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"error": "Not a git repository or git error"}
            
        lines = result.stdout.splitlines()
        changes = []
        for line in lines:
            if len(line) > 3:
                status = line[:2]
                file = line[3:]
                changes.append({"status": status, "file": file})
                
        # Get branch
        branch_res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        branch = branch_res.stdout.strip()
        
        return {
            "branch": branch,
            "changes": changes,
            "clean": len(changes) == 0
        }
    except FileNotFoundError:
        return {"error": "Git not found"}
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Git Inspector")
    parser.add_argument("--mode", default="status", help="Inspection mode")
    args = parser.parse_args()
    
    if args.mode == "status":
        print(json.dumps(get_git_status(), indent=2))
    else:
        print(json.dumps({"error": f"Unknown mode: {args.mode}"}))

if __name__ == "__main__":
    main()
