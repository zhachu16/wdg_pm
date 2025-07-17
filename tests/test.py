from ProjectManager import Project
from pathlib import Path
import shutil

# Clean up from previous runs (for idempotency in testing)
shutil.rmtree("", ignore_errors=True)
shutil.rmtree("../test_archive", ignore_errors=True)

# Setup folders and initial file
test_file_dir = Path("")
test_archive_dir = Path("../test_archive")
test_file_dir.mkdir(exist_ok=True, parents=True)
test_archive_dir.mkdir(exist_ok=True, parents=True)

# Create initial dummy file
file_v1 = test_file_dir / "cube.stl"
file_v1.write_text("version 1 content")

# Initialize Project
project = Project(
    master_id="HAM",
    sub_id=1,
    file=file_v1,
    archive_directory=test_archive_dir,
    status="Created",
    responsible={"manager": ["Alice"], "factory": ["Factory A"]},
    volume=100.0,
    quantity=2
)

# --- Test all updates sequentially ---

# Update master ID
project.update_master_id("HAM_NEW")
assert project.master_id == "HAM_NEW"

# Update status
project.update_status("Printing")
assert project.status == "Printing"

# Update responsible
project.update_responsible("QA", ["Bob", "Charlie"])
assert project.responsible["QA"] == ["Bob", "Charlie"]

# Update quantity
project.update_quantity(5)
assert project.quantity == 5

# Update project name
project.update_name("Special Prototype")
assert project.project_name == "Special Prototype"

# Update customer ID
project.update_customer_id("CUST-001")
assert project.customer_id == "CUST-001"

# Update shipping info
project.update_shipping_info({"Address": "123 Main St", "Post Code": "99999"})
assert project.shipping_info["Post Code"] == "99999"

# Comments
project.add_comment("Initial setup complete.")
project.edit_comment("Corrected initial comment.", 1)
project.remove_comment(1)
assert len(project.comments) == 0

# --- Repeated update_file to test versioning & archiving ---

# Version 2
file_v2 = test_file_dir / "cube_v2.stl"
file_v2.write_text("version 2 content")
project.update_file(file_v2, new_version=True)
assert project.file.name == "cube_v2.stl"
assert (test_archive_dir / "HAM_NEW_1_v1.stl").exists()

# Version 3
file_v3 = test_file_dir / "cube_v3.stl"
file_v3.write_text("version 3 content")
project.update_file(file_v3, new_version=True)
assert project.file.name == "cube_v3.stl"
assert (test_archive_dir / "HAM_NEW_1_v2.stl").exists()

# Version 4
file_v4 = test_file_dir / "cube_v4.stl"
file_v4.write_text("version 4 content")
project.update_file(file_v4, new_version=True)
assert project.file.name == "cube_v4.stl"
assert (test_archive_dir / "HAM_NEW_1_v3.stl").exists()

# Move file and archive directories
new_file_dir = Path("../new_files")
new_archive_dir = Path("../new_archive")
project.update_file_directories(new_file_dir, new_archive_dir)

assert project.file.parent == new_file_dir
assert project.archive_directory == new_archive_dir
assert all(f.parent == new_archive_dir for f in new_archive_dir.iterdir())

# --- Final Review: Change Log + File System Check ---

print("\nFinal Project State:")
print("Project ID:", project.get_project_id())
print("File:", project.file)
print("Archive Directory:", project.archive_directory)
print("Quantity:", project.quantity)
print("Status:", project.status)
print("\nChange Log:")
for key, value in project.change_log.items():
    print(f"{key} -> {value}")

print("\nArchived Files in New Directory:")
for archived_file in new_archive_dir.iterdir():
    print(archived_file.name)
