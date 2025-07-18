import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from config import PROJECTS_DIR, INDEX_FILE
from ProjectManager import ProjectManager
import sys


#TODO: Add update_project button: edit project via the .update_ method
#TODO: Add view button, open project file and view stl


class TextRedirector:
    """
    Redirect stdout and stderr to a Tkinter Text widget.
    """
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        self.widget.insert(tk.END, message)
        self.widget.see(tk.END)

    def flush(self):
        pass  # Required for compatibility with sys.stdout


def get_responsible_dict():
    """
    Prompt user to input responsibility roles and associated people.
    """
    responsible = {}
    while True:
        resp_type = simpledialog.askstring(
            "Responsible Type",
            "Enter responsibility type (e.g., Design, Production) or leave blank to finish:"
        )
        if not resp_type:
            break
        people = simpledialog.askstring(
            "People Responsible",
            f"List people responsible for {resp_type} (comma-separated):"
        )
        responsible[resp_type] = [name.strip() for name in people.split(",")] if people else []
    return responsible


def create_project():
    """
    Prompt user for project creation details and create a new project via ProjectManager.
    Stops and shows a warning if any required field is empty.
    """
    master_id = simpledialog.askstring("Input", "Master ID (e.g., HAM, MAAS)")
    if not master_id:
        messagebox.showwarning("Missing Input", "Master ID is required.")
        return

    sub_id = simpledialog.askinteger("Input", "Sub ID (e.g., 1, 2)")
    if sub_id is None:
        messagebox.showwarning("Missing Input", "Sub ID is required.")
        return

    messagebox.showinfo("Select Project File", "Only .stl or .obj files are supported.")
    file_path = filedialog.askopenfilename(title="Select .stl or .obj File")
    if not file_path:
        messagebox.showwarning("Missing Input", "A project file is required.")
        return

    messagebox.showinfo("Select Archive Directory", "Select the directory where archived files are stored.")
    archive_dir = filedialog.askdirectory()
    if not archive_dir:
        messagebox.showwarning("Missing Input", "An archive directory is required.")
        return

    responsible = get_responsible_dict()

    quantity = simpledialog.askinteger("Input", "Quantity to produce")
    if quantity is None:
        messagebox.showwarning("Missing Input", "Quantity is required.")
        return

    pm.create_project(master_id, sub_id, file_path, archive_dir, responsible, quantity)
    refresh_project_list()


def refresh_project_list():
    """
    Refresh the displayed list of projects in the Listbox.
    """
    listbox.delete(0, tk.END)
    for pid in pm.get_project_list():
        listbox.insert(tk.END, pid)


def show_project_info():
    """
    Display detailed information about the selected project.
    """
    selected = listbox.get(tk.ACTIVE)
    if not selected:
        return
    info = pm.get_project_info(selected)
    info_str = "\n".join(f"{k}: {v}" for k, v in info.items())
    messagebox.showinfo(f"Project Info: {selected}", info_str)


def delete_project():
    """
    Delete the selected project after confirmation from the user.
    """
    selected = listbox.get(tk.ACTIVE)
    if not selected:
        messagebox.showwarning("No Selection", "Select a project to delete.")
        return
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected}'?")
    if confirm:
        pm.delete_project(selected)
        refresh_project_list()


# --- Initialize ProjectManager ---
pm = ProjectManager(index_file=INDEX_FILE, projects_dir=PROJECTS_DIR)

# --- GUI Setup ---
root = tk.Tk()
root.title("Project Manager GUI")

btn_create = tk.Button(root, text="Create Project", command=create_project)
btn_create.pack()

btn_refresh = tk.Button(root, text="Refresh Project List", command=refresh_project_list)
btn_refresh.pack()

listbox = tk.Listbox(root)
listbox.pack(fill=tk.BOTH, expand=True)

btn_info = tk.Button(root, text="Show Project Info", command=show_project_info)
btn_info.pack()

btn_delete = tk.Button(root, text="Delete Project", command=delete_project)
btn_delete.pack()

log_frame = tk.Frame(root)
log_frame.pack(fill=tk.BOTH, expand=True)

log_label = tk.Label(log_frame, text="Console Output:")
log_label.pack(anchor="w")

log_text = tk.Text(log_frame, height=10, bg="black", fg="white")
log_text.pack(fill=tk.BOTH, expand=True)

# Redirect stdout and stderr to the GUI console
sys.stdout = TextRedirector(log_text)
sys.stderr = TextRedirector(log_text)

# Populate the project list initially
refresh_project_list()

# Start the GUI event loop
root.mainloop()
