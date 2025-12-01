import os
import json
import argparse
import sys

def is_binary_file(filepath, chunk_size=1024):
    """Check if file is binary by looking for null bytes in the first chunk."""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(chunk_size)
            if b'\0' in chunk:
                return True
    except Exception:
        pass
    return False

def count_lines(filepath, encoding):
    """Count total lines in file efficiently."""
    count = 0
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            for _ in f:
                count += 1
    except Exception:
        pass
    return count

def read_file(filepath, offset, limit):
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}
    
    if is_binary_file(filepath):
        return {
            "content": None,
            "lines_read": 0,
            "total_lines": 0,
            "truncated": False,
            "is_binary": True
        }

    encodings = ['utf-8', sys.getdefaultencoding(), 'latin-1']
    content = ""
    lines_read = 0
    total_lines = 0
    encoding_used = None
    
    # Try encodings
    for enc in encodings:
        try:
            total_lines = count_lines(filepath, enc)
            with open(filepath, 'r', encoding=enc) as f:
                # Skip to offset
                for _ in range(offset):
                    next(f, None)
                
                # Read limit lines
                lines = []
                for _ in range(limit):
                    line = next(f, None)
                    if line is None:
                        break
                    lines.append(line)
                
                content = "".join(lines)
                lines_read = len(lines)
                encoding_used = enc
                break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return {"error": str(e)}
            
    if encoding_used is None:
         return {
            "content": None,
            "lines_read": 0,
            "total_lines": 0,
            "truncated": False,
            "is_binary": True,
            "note": "Failed to decode text with common encodings"
        }

    truncated = (offset + lines_read) < total_lines

    return {
        "content": content,
        "lines_read": lines_read,
        "total_lines": total_lines,
        "truncated": truncated,
        "is_binary": False,
        "encoding": encoding_used
    }

def main():
    parser = argparse.ArgumentParser(description="Safe File Reader")
    parser.add_argument("--path", required=True, help="File path to read")
    parser.add_argument("--offset", type=int, default=0, help="Start line (0-indexed)")
    parser.add_argument("--limit", type=int, default=1000, help="Max lines to read")
    
    args = parser.parse_args()
    
    result = read_file(args.path, args.offset, args.limit)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
