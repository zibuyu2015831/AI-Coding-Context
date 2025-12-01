import sys
import json
import subprocess
import platform

def check_node_version():
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None

def main():
    python_version = sys.version.split()[0]
    node_version = check_node_version()
    
    os_info = f"{platform.system()} {platform.release()}"
    
    status = {
        "python": {
            "version": python_version,
            "path": sys.executable,
            "ok": sys.version_info >= (3, 6)
        },
        "node": {
            "version": node_version,
            "ok": False # Will be updated if node is found and version is sufficient
        },
        "os": os_info
    }
    
    if node_version:
        # Parse v14.17.0 -> 14
        try:
            major_version = int(node_version.lstrip('v').split('.')[0])
            status["node"]["ok"] = major_version >= 14
        except ValueError:
            pass

    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
