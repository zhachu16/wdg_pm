import hashlib
import pickle
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Union
from pathlib import Path
import shutil
import pandas as pd


# TODO: Implement _update_volume() method
# TODO: Implement check_feasibility() method --> checks if the model is 3D printable


@dataclass
class Project:
    """
    Represents a 3D printing project with comprehensive tracking of versions,
    responsibilities, status updates, and change history.

    Attributes:
        master_id (str): Master project identifier (e.g., "HAM", "MAAS", "3DD")
        sub_id (int): Sub-identifier for each printing job (e.g., 1, 2, 3)
        file (Path): Path to the current print file (.stl or .obj). Must include directory and filename.
        archive_directory (Path): Directory for storing archived versions of print files.
        status (str): Current project status. Defaults to 'Created'.
        responsible (Dict[str, List[str]]): Dictionary mapping responsibility types to individuals.
        quantity (int): Number of copies to be printed.
        volume (float): Volume for cost calculation, in cubic units.

        Optional:
        project_name (Optional[str]): Human-readable project name.
        customer_id (Optional[str]): Identifier for the customer.
        shipping_info (Optional[Dict[str, Union[str, int]]]): Shipping details.
        comments (Dict[str, str]): Comments with timestamps.
    """

    # Required
    master_id: str
    sub_id: int
    file: Path
    archive_directory: Path
    responsible: Dict[str, List[str]]
    quantity: int
    volume: float = 0.0
    status: str = 'Created'

    # Optional
    project_name: Optional[str] = None
    customer_id: Optional[str] = None
    shipping_info: Optional[Dict[str, Union[str, int]]] = None
    comments: Dict[str, str] = field(default_factory=dict)
    _comment_id: int = 0

    # Change log
    change_log: Dict[str, str] = field(default_factory=dict)

    # Change counters
    _file_version: int = 1
    _id_change_count: int = 0
    _file_change_count: int = 0
    _status_change_count: int = 0
    _responsible_change_count: int = 0
    _quantity_change_count: int = 0
    _name_change_count: int = 0
    _customer_change_count: int = 0
    _shipping_info_change_count: int = 0
    _comment_change_count: int = 0

    def get_project_id(self) -> str:
        """Return the unique project ID as master_id_sub_id."""
        return f"{self.master_id}_{self.sub_id}"

    def get_file_version(self) -> str:
        """Return the file version string."""
        return f"{self.get_project_id()}_v{self._file_version}"

    def add_comment(self, comment: str) -> None:
        """Add a timestamped comment."""
        self._comment_change_count += 1
        self._comment_id += 1
        timestamp = datetime.now().isoformat()
        self.comments[f"comment_{self._comment_id}"] = f"{timestamp}: {comment}"
        self.change_log[f"Comment Change #{self._comment_change_count}"] = (
            f"{timestamp}: comment_{self._comment_id} added"
        )

    def remove_comment(self, comment_id: int) -> None:
        """Remove a comment by its comment_id."""
        key = f"comment_{comment_id}"
        if key not in self.comments:
            raise KeyError(f"Comment {comment_id} not found")
        self._comment_change_count += 1
        timestamp = datetime.now().isoformat()
        del self.comments[key]
        self.change_log[f"Comment Change #{self._comment_change_count}"] = (
            f"{timestamp}: Comment {comment_id} deleted"
        )

    def edit_comment(self, updated_comment: str, comment_id: int) -> None:
        """Edit an existing comment."""
        key = f"comment_{comment_id}"
        if key not in self.comments:
            raise KeyError(f"Comment {comment_id} not found")
        self._comment_change_count += 1
        timestamp = datetime.now().isoformat()
        self.comments[key] = f"edited {timestamp}: {updated_comment}"
        self.change_log[f"Comment Change #{self._comment_change_count}"] = (
            f"{timestamp}: Comment {comment_id} edited"
        )

    def update_master_id(self, new_master_id: str) -> None:
        """Update the master project ID."""
        self._id_change_count += 1
        timestamp = datetime.now().isoformat()
        old_project_id = self.get_project_id()
        self.master_id = new_master_id
        new_project_id = self.get_project_id()
        self.change_log[f"Project ID Change #{self._id_change_count}"] = (
            f"{timestamp}: Subproject moved under master project {new_master_id}. "
            f"Project ID changed from {old_project_id} to {new_project_id}"
        )

    def update_file(self, new_file: str, new_version: bool = False) -> None:
        """Update the file path, optionally versioning it."""
        new_file = Path(new_file)
        if not new_file.exists():
            raise FileNotFoundError(f"File {new_file} does not exist")
        if new_file == self.file:
            raise ValueError("New file cannot be the same as current file")
        self._file_change_count += 1
        timestamp = datetime.now().isoformat()

        if new_version:
            archived_filename = f"{self.get_file_version()}{self.file.suffix}"
            archived_path = self.archive_directory / archived_filename
            self.archive_directory.mkdir(parents=True, exist_ok=True)
            shutil.move(str(self.file), str(archived_path))
            self._file_version += 1
            self.file = new_file
            self._update_volume()
            self.change_log[f"Project File Change #{self._file_change_count}"] = (
                f"{timestamp}: File version updated to {self.get_file_version()}, new volume {self.volume}"
            )
        else:
            self.file = new_file
            self._update_volume()
            self.change_log[f"Project File Change #{self._file_change_count}"] = (
                f"{timestamp}: File updated (same version), new volume {self.volume}"
            )

    def update_file_directories(self, new_file_path: Optional[str] = None, new_archive_path: Optional[str] = None) -> None:
        """Update the directories for active files and archive."""
        if new_file_path is None and new_archive_path is None:
            raise ValueError("Must provide at least one new path")
        timestamp = datetime.now().isoformat()

        if new_file_path is not None:
            new_file_path = Path(new_file_path)
            self._file_change_count += 1
            new_file_path.mkdir(parents=True, exist_ok=True)
            target_file = new_file_path / self.file.name
            shutil.move(str(self.file), str(target_file))
            self.file = target_file
            self.change_log[f"Project File Change #{self._file_change_count}"] = (
                f"{timestamp}: File directory changed to {new_file_path}"
            )
        if new_archive_path is not None:
            new_archive_path = Path(new_archive_path)
            self._file_change_count += 1
            new_archive_path.mkdir(parents=True, exist_ok=True)
            for archived_file in self.archive_directory.iterdir():
                if archived_file.is_file():
                    target_file = new_archive_path / archived_file.name
                    shutil.move(str(archived_file), str(target_file))
            self.archive_directory = new_archive_path
            self.change_log[f"Project File Change #{self._file_change_count}"] = (
                f"{timestamp}: Archive directory changed to {new_archive_path}"
            )

    def update_status(self, new_status: str) -> None:
        """Update the status of the project."""
        self._status_change_count += 1
        timestamp = datetime.now().isoformat()
        self.status = new_status
        self.change_log[f"Status Change #{self._status_change_count}"] = (
            f"{timestamp} Status changed to {new_status}"
        )

    def update_responsible(self, responsible_type: str, responsible: List[str]) -> None:
        """Update the responsible persons for a specific responsibility type."""
        self._responsible_change_count += 1
        timestamp = datetime.now().isoformat()
        self.responsible[responsible_type] = responsible
        self.change_log[f"Responsible Change #{self._responsible_change_count}"] = (
            f"{timestamp}: {responsible_type} updated to {responsible}"
        )

    def _update_volume(self) -> None:
        """Update the volume from the 3D file (currently placeholder)."""
        # TODO: Implement actual 3D model volume extraction.
        self.volume = 0.0  # Placeholder

    def update_quantity(self, new_quantity: int) -> None:
        """Update the quantity to produce."""
        self._quantity_change_count += 1
        timestamp = datetime.now().isoformat()
        self.quantity = new_quantity
        self.change_log[f"Quantity Change #{self._quantity_change_count}"] = (
            f"{timestamp}: Quantity updated to {new_quantity}"
        )

    def update_name(self, new_name: str) -> None:
        """Update the project name."""
        self._name_change_count += 1
        timestamp = datetime.now().isoformat()
        self.project_name = new_name
        self.change_log[f"Name Change #{self._name_change_count}"] = (
            f"{timestamp} Project name updated to {new_name}"
        )

    def update_customer_id(self, new_customer_id: str):
        """Update the customer ID."""
        self._customer_change_count += 1
        timestamp = datetime.now().isoformat()
        self.customer_id = new_customer_id
        self.change_log[f"Customer ID Change #{self._customer_change_count}"] = (
            f"{timestamp} Project customer updated to {new_customer_id}"
        )

    def update_shipping_info(self, new_shipping_info: dict):
        """Update the shipping information."""
        self._shipping_info_change_count += 1
        timestamp = datetime.now().isoformat()
        self.shipping_info = new_shipping_info
        post_code = new_shipping_info.get('Post Code', 'Unknown')
        self.change_log[f"Shipping Info Change #{self._shipping_info_change_count}"] = (
            f"{timestamp} Shipping info updated to {post_code}"
        )

    def print_comments(self) -> None:
        """Print all comments."""
        if not self.comments:
            print("No comments.")
            return
        print(f"\nComments for project {self.get_project_id()}:")
        for comment_id, comment_text in sorted(self.comments.items()):
            print(f"  {comment_id}: {comment_text}")

    def print_change_log(self) -> None:
        """Print the change log."""
        if not self.change_log:
            print("No change log entries.")
            return
        print(f"\nChange log for project {self.get_project_id()}:")
        for log_id, log_entry in sorted(self.change_log.items()):
            print(f"  {log_id}: {log_entry}")

    def get_info(self) -> dict:
        """Return all available attributes as a dictionary."""
        return {
            "Project ID": self.get_project_id(),
            "Project Name": self.project_name,
            "Customer ID": self.customer_id,
            "Status": self.status,
            "Quantity": self.quantity,
            "Volume": self.volume,
            "File": self.file,
            "Archive Directory": self.archive_directory,
            "Responsible": self.responsible,
            "Shipping Info": self.shipping_info,
            "Comments": self.comments
        }

    def print_info(self, comment: bool = False, change_log: bool = False) -> None:
        """Print all available attributes and optionally the change log."""
        info = self.get_info()
        print(f"\n--- Project Info for {info['Project ID']} ---")
        for key, value in info.items():
            if key != "Project ID" and key != "Comments":
                print(f"{key}: {value}")
        if comment:
            self.print_comments()
        if change_log:
            self.print_change_log()



class ProjectManager:
    def __init__(self, index_file: Path, projects_dir: Path):
        self.index_file = index_file
        self.projects_dir = projects_dir
        self.projects_index = pd.DataFrame(columns=["project_id", "filename", "status"]).set_index("project_id")
        self._load_index()

    def _project_path(self, project_id: str, create_if_missing: bool = False) -> Path:
        if project_id not in self.projects_index.index:
            if create_if_missing:
                hash_str = hashlib.md5(project_id.encode()).hexdigest()
                filename = f"{hash_str}.pkl"
                self.projects_index.loc[project_id] = [filename, "Created"]

            else:
                raise KeyError(f"[ERROR] Project ID '{project_id}' not found in index.")

        filename = self.projects_index.loc[project_id, "filename"]
        return self.projects_dir / filename

    def _load_index(self) -> None:
        if self.index_file.exists():
            try:
                with open(self.index_file, "rb") as f:
                    self.projects_index = pickle.load(f)

            except Exception as e:
                print(f"[ERROR] Failed to load project index: {e}")

    def _update_index(self) -> None:
        try:
            self.index_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file = self.index_file.with_suffix(".tmp")

            with open(temp_file, "wb") as f:
                pickle.dump(self.projects_index, f)
            os.replace(temp_file, self.index_file)

        except Exception as e:
            print(f"[ERROR] Failed to save project index: {e}")

    def create_project(
        self,
        master_id: str,
        sub_id: int,
        file: str,
        archive_directory: str,
        responsible: Dict[str, List[str]],
        quantity: int = 1
    ) -> None:
        project = Project(
            master_id=master_id,
            sub_id=sub_id,
            file=Path(file),
            archive_directory=Path(archive_directory),
            responsible=responsible,
            quantity=quantity,
        )
        project_id = project.get_project_id()
        if project_id in self.projects_index.index:
            print(f"[ERROR] Cannot create duplicate project: '{project_id}' already exists.")
            return

        project_path = self._project_path(project_id, create_if_missing=True)
        self.projects_index.loc[project_id, "status"] = project.status
        self.projects_index.loc[project_id, "filename"] = project_path.name

        try:
            project_path.parent.mkdir(parents=True, exist_ok=True)

            with open(project_path, "wb") as f:
                pickle.dump(project, f)
            self._update_index()
            print(f"[INFO] Project {project_id} created and saved successfully.")

        except Exception as e:
            print(f"[ERROR] Failed to create project {project_id}: {e}")

    def delete_project(self, project_id: str) -> None:
        if project_id not in self.projects_index.index:
            print(f"[WARNING] Project ID '{project_id}' not found. Nothing to delete.")
            return

        try:
            project_file = self._project_path(project_id)
            if project_file.exists():
                project_file.unlink()
                print(f"[INFO] Deleted project file for '{project_id}'.")
            else:
                print(f"[WARNING] Project file for '{project_id}' does not exist on disk.")
        except Exception as e:
            print(f"[ERROR] Failed to delete project file for '{project_id}': {e}")
            return

        self.projects_index.drop(project_id, inplace=True)
        try:
            self._update_index()
            print(f"[INFO] Project '{project_id}' removed from index.")
        except Exception as e:
            print(f"[ERROR] Failed to update project index after deletion: {e}")

    def _get_project(self, project_id: str) -> Optional["Project"]:
        if project_id not in self.projects_index.index:
            print(f"[WARNING] Project ID '{project_id}' not found.")
            return None

        try:
            with open(self._project_path(project_id), "rb") as f:
                return pickle.load(f)

        except Exception as e:
            print(f"[ERROR] Failed to load project {project_id}: {e}")
            return None

    def update_project(self, project_id: str, action: str, info: Union[str, int, float, dict, list]) -> None:
        project = self._get_project(project_id)
        if not project:
            print(f"[ERROR] Project {project_id} could not be loaded.")
            return

        method = getattr(project, action, None)
        if not method or not callable(method):
            print(f"[ERROR] Action '{action}' not valid for Project.")
            return

        try:
            if isinstance(info, dict):
                method(**info)
            elif isinstance(info, (list, tuple)):
                method(*info)
            else:
                method(info)
        except Exception as e:
            print(f"[ERROR] Failed to apply '{action}' to {project_id}: {e}")
            return

        self.projects_index.loc[project_id, "status"] = project.status

        try:
            with open(self._project_path(project_id), "wb") as f:
                pickle.dump(project, f)
            self._update_index()
            print(f"[INFO] Project {project_id} updated successfully via '{action}'.")
        except Exception as e:
            print(f"[ERROR] Failed to save updated project {project_id}: {e}")

    def get_project_list(self) -> List[str]:
        return self.projects_index.index.tolist()

    def get_project_info(self, project_id: str) -> dict:
        project = self._get_project(project_id)
        return project.get_info()

    def print_project_info(self, project_id: str, comment: bool = False, change_log: bool = False) -> None:
        project = self._get_project(project_id)
        project.print_info(comment=comment, change_log=change_log)
