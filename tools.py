from pathlib import Path

ALLOWED_EXTENSIONS = {".py", ".md", ".txt"}
IGNORE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}


def list_files():
    files = []

    for path in Path(".").rglob("*"):
        if not path.is_file():
            continue

        # skip system dirs
        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        # skip db / junk
        if path.name.endswith(".sqlite") or path.name.endswith(".db"):
            continue

        # allow only code/text
        if path.suffix not in ALLOWED_EXTENSIONS:
            continue

        files.append(str(path))

    return files


def read_file(path: str):
    try:
        # safety guard
        if ".venv" in path or "__pycache__" in path:
            return "IGNORED SYSTEM FILE"

        with open(path, "r") as f:
            return f.read()[:8000]  # hard cap

    except Exception as e:
        return str(e)


def write_file(path: str, content: str):
    path_obj = Path(path)

    # 🔥 auto-create directories
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(path_obj, "w") as f:
        f.write(content)

    return f"FILE WRITTEN: {path}"