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
project.update_file("cube_v2.stl", new_version=True)


# Version 3
file_v3 = test_file_dir / "cube_v3.stl"
file_v3.write_text("version 3 content")
project.update_file("cube_v3.stl", new_version=True)


# Version 4
file_v4 = test_file_dir / "cube_v4.stl"
file_v4.write_text("version 4 content")
project.update_file("cube_v4.stl", new_version=True)

file_v4 = test_file_dir / "cube_v4_1.stl"
file_v4.write_text("version 4_1 content")
project.update_file("cube_v4_1.stl", new_version=False)

# Move file and archive directories
new_file_dir = Path("../new_files")
new_archive_dir = Path("../new_archive")
project.update_file_directories("/Users/zhachu16/Documents/Wedge/wdg_pm/tests/test_file", "/Users/zhachu16/Documents/Wedge/wdg_pm/tests/test_archive")


# --- Final Review: Change Log + File System Check ---
project.print_info(comment=True, change_log=True)

