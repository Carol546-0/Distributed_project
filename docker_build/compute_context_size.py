import os
import sys


def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T']:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Patterns we'll explicitly exclude when estimating build context
EXCLUDE_DIRS = {'.venv', 'data', '__pycache__', '.git', '.vscode', 'model_cache', 'hf_models'}
EXCLUDE_SUFFIXES = {'.pyc', '.pt', '.bin', '.onnx', '.db', '.tar.gz', '.pth'}


def is_excluded(relpath):
    parts = relpath.split(os.sep)
    for d in EXCLUDE_DIRS:
        if d in parts:
            return True, d
    for suf in EXCLUDE_SUFFIXES:
        if relpath.lower().endswith(suf):
            return True, suf
    return False, None


def main():
    total = 0
    excluded = 0
    excluded_breakdown = {}

    for dirpath, dirnames, filenames in os.walk(ROOT):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            try:
                sz = os.path.getsize(full)
            except OSError:
                continue

            rel = os.path.relpath(full, ROOT)
            total += sz

            excl, key = is_excluded(rel)
            if excl:
                excluded += sz
                excluded_breakdown.setdefault(key, 0)
                excluded_breakdown[key] += sz

    included = total - excluded

    print(f"ROOT={ROOT}")
    print(f"TOTAL_BYTES={total}")
    print(f"TOTAL_HUMAN={sizeof_fmt(total)}")
    print(f"EXCLUDED_BYTES={excluded}")
    print(f"EXCLUDED_HUMAN={sizeof_fmt(excluded)}")
    print(f"INCLUDED_BYTES={included}")
    print(f"INCLUDED_HUMAN={sizeof_fmt(included)}")
    print("---EXCLUDED_BREAKDOWN---")
    for k, v in sorted(excluded_breakdown.items(), key=lambda x: -x[1]):
        print(f"{k}: {v} ({sizeof_fmt(v)})")


if __name__ == '__main__':
    main()
