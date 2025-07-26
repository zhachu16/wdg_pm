from pathlib import Path

BASE_DIR = Path("/Users/zhachu16/Documents/Wedge/wdg_pm/")/ "tests/GUI_test"
PROJECTS_DIR = BASE_DIR / "projects"
INDEX_FILE = BASE_DIR / "project_index.pkl"
UPDATE_METHODS = ["update_master_id", "update_sub_id", "update_file", "update_file_directories", "update_status",
                  "update_quantity", "update_responsibility", "delete_responsibility", "update_name",
                  "update_customer_id", "update_shipping_info"]
RHINO_DIR = ""
VIEW_METHODS = ["default", "rhino"]
COMMENT_ACTIONS = ["add_comments", "remove_comments", "edit_comment"]