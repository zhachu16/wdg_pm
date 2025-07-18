from pathlib import Path
from config import INDEX_FILE, PROJECTS_DIR
from ProjectManager import ProjectManager

# Initialize ProjectManager
pm = ProjectManager(index_file=INDEX_FILE, projects_dir=PROJECTS_DIR)

master_id = "MAAS"

# Paths
project1_file = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/projects/HAM_1/cube.stl")
project2_file = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/projects/HAM_2/sphere.stl")
project2_new_file = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/sphere_new.stl")
project2_archive = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/projects/HAM_2/archive")
project2_new_archive = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/projects/HAM_2/archive_new")
project1_archive = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/ProjectManager_test/projects/HAM_1/archive")

responsible = {"Design": ["Alice"], "Print": ["Bob"]}

# ---------------------------
# Test 1: Create Project 1 and 2
# ---------------------------
pm.create_project(
    master_id="HAM",
    sub_id=1,
    file=str(project1_file),
    archive_directory=str(project1_archive),
    responsible=responsible,
    quantity=1
)

pm.create_project(
    master_id="HAM",
    sub_id=2,
    file=str(project2_file),
    archive_directory=str(project2_archive),
    responsible=responsible,
    quantity=2
)

print("\n[After Test 1]: Project List:")
print(pm.get_project_list())


# ---------------------------
# Test 2: Comments, file updates, shipping info
# ---------------------------
# Project 1: Comments and name updates
pm.update_project("HAM_1", "add_comment", "First comment.")
pm.update_project("HAM_1", "add_comment", "Second comment.")
pm.update_project("HAM_1", "edit_comment", {"updated_comment": "Updated second comment.", "comment_id": 2})
pm.update_project("HAM_1", "update_name", "Cube Project")
pm.update_project("HAM_1", "remove_comment", 1)

# Project 2: File update (new version) and shipping info
pm.update_project("HAM_2", "update_file", {"new_file": str(project2_new_file), "new_version": True})
pm.update_project("HAM_2", "update_shipping_info", {"new_shipping_info": {"Post Code": "12345", "Address": "42 Wallaby Way"}})


print("\n[After Test 2]: Project List:")
print(pm.get_project_list())


# ---------------------------
# Test 3: Print Info
# ---------------------------
print("\n[Project 1 Info]:")
pm.print_project_info("HAM_1", comment=True, change_log=False)

print("\n[Project 2 Info]:")
pm.print_project_info("HAM_2", comment=True, change_log=True)

# Update project 2 archive directory
pm.update_project("HAM_2", "update_file_directories", {"new_archive_path": str(project2_new_archive)})


# ---------------------------
# Test 4: Print Project List
# ---------------------------
print("\n[After Test 4]: Project List:")
print(pm.get_project_list())


# ---------------------------
# Test 5: Delete Project 1
# ---------------------------
pm.delete_project("HAM_1")

print("\n[After Test 5]: Project List:")
print(pm.get_project_list())


# ---------------------------
# Test 6: Final Project List
# ---------------------------
print("\n[After Test 6]: Final Project List:")
print(pm.get_project_list())
