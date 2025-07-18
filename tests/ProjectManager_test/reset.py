import shutil
from pathlib import Path

# Paths as before test
project2_original_file = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/projects/HAM_2/sphere.stl")
project2_new_file = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/sphere_new.stl")
project2_archive_dir = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/projects/HAM_2/archive")
project2_new_archive_dir = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/projects/HAM_2/archive_new")

# 1. Move sphere_new.stl back to sphere.stl location
if project2_new_file.exists():
    target_file = project2_original_file
    target_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(project2_new_file), str(target_file))
    print(f"[INFO] Moved {project2_new_file} -> {target_file}")
else:
    print(f"[INFO] {project2_new_file} does not exist, skipping file move.")

# 2. Restore sphere_new.stl from sphere.stl (make a fresh copy for future tests)
if project2_original_file.exists():
    shutil.copy2(str(project2_original_file), str(project2_new_file))
    print(f"[INFO] Copied {project2_original_file} -> {project2_new_file}")

# 3. Move all files from new archive dir back to old archive dir
if project2_new_archive_dir.exists() and project2_new_archive_dir.is_dir():
    for file in project2_new_archive_dir.iterdir():
        if file.is_file():
            target = project2_archive_dir / file.name
            project2_archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(target))
            print(f"[INFO] Moved {file} -> {target}")

    try:
        project2_new_archive_dir.rmdir()
        print(f"[INFO] Removed empty directory {project2_new_archive_dir}")
    except OSError:
        print(f"[WARNING] Directory {project2_new_archive_dir} is not empty or cannot be removed.")
else:
    print(f"[INFO] {project2_new_archive_dir} does not exist, skipping archive move.")

# 4. Delete all files in archive directory
if project2_archive_dir.exists() and project2_archive_dir.is_dir():
    for file in project2_archive_dir.iterdir():
        if file.is_file():
            file.unlink()
            print(f"[INFO] Deleted {file}")

print("\n[RESET COMPLETED]")
