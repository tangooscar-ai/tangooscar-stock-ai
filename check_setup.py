import sys
from pathlib import Path

print(f"Python version : {sys.version.split()[0]}")

in_venv = sys.prefix != sys.base_prefix
print(f"Virtual env    : {'ACTIVE' if in_venv else 'NOT ACTIVE'}")

required = ["config", "data/raw", "data/processed", "src/data",
            "src/analysis", "src/storage", "src/utils",
            "tests", "models", "reports"]
missing = [p for p in required if not Path(p).is_dir()]
print(f"Folders        : {'all present' if not missing else 'MISSING ' + str(missing)}")

init_name = chr(95) * 2 + "init" + chr(95) * 2 + ".py"
pkg_folders = ["src", "src/data", "src/analysis", "src/storage", "src/utils"]
missing_inits = [f"{d}/{init_name}" for d in pkg_folders
                 if not (Path(d) / init_name).is_file()]
print(f"Package files  : {'all present' if not missing_inits else 'MISSING ' + str(missing_inits)}")

gi = Path(".gitignore").read_text() if Path(".gitignore").exists() else ""
env_ignored = ".env" in gi.splitlines()
print(f".env protected : {'YES' if env_ignored else 'NO - add .env to .gitignore'}")

ok = (in_venv and not missing and not missing_inits and env_ignored
      and (3, 10) <= sys.version_info[:2] <= (3, 12))
print("\nPHASE 1 COMPLETE" if ok else "\nFIX THE ITEMS ABOVE")