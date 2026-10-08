import pathlib
import re
import subprocess
from datetime import datetime
from typing import Tuple

from langchain_core.tools import tool

PROJECTS_ROOT = pathlib.Path.cwd() / "generated_projects"
PROJECT_ROOT = PROJECTS_ROOT / "default_project"


def _slugify_project_name(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "project"


def get_project_root() -> pathlib.Path:
    return PROJECT_ROOT


def set_project_root(project_name: str) -> str:
    """Selects a unique output folder for the current generated project."""
    global PROJECT_ROOT
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    PROJECT_ROOT = PROJECTS_ROOT / f"{_slugify_project_name(project_name)}-{timestamp}"
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    return str(PROJECT_ROOT)


def safe_path_for_project(path: str) -> pathlib.Path:
    project_root = get_project_root().resolve()
    p = (project_root / path).resolve()
    if project_root not in p.parents and project_root != p.parent and project_root != p:
        raise ValueError("Attempt to write outside project root")
    return p


@tool
def write_file(path: str, content: str) -> str:
    """Writes content to a file at the specified path within the project root."""
    p = safe_path_for_project(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return f"WROTE:{p}"


@tool
def read_file(path: str) -> str:
    """Reads content from a file at the specified path within the project root."""
    p = safe_path_for_project(path)
    if not p.exists():
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


@tool
def get_current_directory() -> str:
    """Returns the current working directory."""
    return str(get_project_root())


@tool
def list_files(directory: str = ".") -> str:
    """Lists all files in the specified directory within the project root."""
    p = safe_path_for_project(directory)
    if not p.is_dir():
        return f"ERROR: {p} is not a directory"
    files = [str(f.relative_to(get_project_root())) for f in p.glob("**/*") if f.is_file()]
    return "\n".join(files) if files else "No files found."

@tool
def run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
    """Runs a shell command in the specified directory and returns the result."""
    cwd_dir = safe_path_for_project(cwd) if cwd else get_project_root()
    res = subprocess.run(cmd, shell=True, cwd=str(cwd_dir), capture_output=True, text=True, timeout=timeout)
    return res.returncode, res.stdout, res.stderr


def init_project_root():
    get_project_root().mkdir(parents=True, exist_ok=True)
    return str(get_project_root())
