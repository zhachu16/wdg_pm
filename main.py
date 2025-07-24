import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from config import PROJECTS_DIR, INDEX_FILE, UPDATE_METHODS
from ProjectManager import ProjectManager
import sys


#TODO: Add view button, open project file and view stl
#TODO: Add edit comment button

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


def get_responsibility_dict(single_pair: bool=False):
    """
    Prompt user to input responsibility roles and associated people/companies.
    """
    if single_pair:
        resp_type = simpledialog.askstring("Responsibility Type",
                                           "Enter responsibility type (e.g. Designer, Factory, Shipping):",
                                           parent=root)
        if not resp_type:
            return

        people_str = simpledialog.askstring(
            "People Responsible",
            f"List people/companies responsible for {resp_type} (comma separated), or leave blank to abort:",
            parent=root
        )
        if people_str is None:
            return
        people_list = [name.strip() for name in people_str.split(",") if name.strip()]
        if not people_list:
            return

        responsibility = {"responsibility_type": resp_type, "responsible": people_list}
        return responsibility

    else:
        responsibility = {}
        while True:
            resp_type = simpledialog.askstring(
                "responsibility Type",
                "Enter responsibility type (e.g., Design, Production) or leave blank to finish:"
            )
            if not resp_type:
                break
            people = simpledialog.askstring(
                "People Responsible",
                f"List people/company responsible for {resp_type} (comma-separated):"
            )
            responsibility[resp_type] = [name.strip() for name in people.split(",")] if people else []
        return responsibility


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

    messagebox.showinfo("Project File", "Select Project file")
    file_path = filedialog.askopenfilename(title="Select .stl or .obj File")
    if not file_path:
        messagebox.showwarning("Missing Input", "A project file is required.")
        return

    messagebox.showinfo("Archive Directory", "Select the directory where archived files are stored.")
    archive_dir = filedialog.askdirectory()
    if not archive_dir:
        messagebox.showwarning("Missing Input", "An archive directory is required.")
        return

    responsibility = get_responsibility_dict()

    quantity = simpledialog.askinteger("Input", "Quantity to produce")
    if quantity is None:
        messagebox.showwarning("Missing Input", "Quantity is required.")
        return

    pm.create_project(master_id, sub_id, file_path, archive_dir, responsibility, quantity)
    refresh_project_list()


def edit():
    selected = listbox.get(tk.ACTIVE)
    if not selected:
        messagebox.showwarning("No Selection", "Select a project to edit.")
        return

    # --- Create a popup window for selection ---
    popup = tk.Toplevel(root)
    popup.title("Select Update Method")
    popup.geometry("300x200")
    popup.grab_set()  # Modal window

    tk.Label(popup, text="Select method to update:").pack(pady=10)

    selected_method = tk.StringVar(popup)
    selected_method.set(UPDATE_METHODS[0])  # Default selection

    tk.OptionMenu(popup, selected_method, *UPDATE_METHODS).pack(pady=5)

    def on_confirm():
        action = selected_method.get()
        popup.destroy()

        # Handle 'update_responsibility' separately
        if action == "update_responsibility":
            info = get_responsibility_dict(single_pair=True)
            if info:
                pm.update_project(selected, action, info)
                refresh_project_list()
            return

        elif action == "update_file":
            messagebox.showinfo("Project File", "Select new project file")
            new_file = filedialog.askopenfilename(title="Select .stl or .obj File")
            if not new_file:
                messagebox.showwarning("Missing Input", "A project file is required.")
                return
            new_version = messagebox.askyesno("New Version", "Is this a new version?")
            info = {"new_file": new_file, "new_version": new_version}

        elif action == "update_file_directories":
            update_file_dir = messagebox.askyesno("New File path",
                                                  "Do you wish to update file directories?")
            if update_file_dir:
                new_file_path = filedialog.askdirectory(title="Select new file directories")
            else:
                new_file_path = None

            update_archive_dir = messagebox.askyesno("New archive path",
                                                     "Do you wish to update archive directories?")
            if update_archive_dir:
                new_archive_path = filedialog.askdirectory(title="Select new archive directories")
            else:
                new_archive_path = None

            info = {"new_file_path": new_file_path, "new_archive_path": new_archive_path}

        else:
            # Default: ask for a single value
            info_str = simpledialog.askstring("New Value", f"Enter new value for '{action}':", parent=root)
            if info_str is None:
                return

            try:
                info = eval(info_str, {"__builtins__": {}})
            except Exception:
                info = info_str

        pm.update_project(selected, action, info)
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


def get_project_change_log():
    """"""
    selected = listbox.get(tk.ACTIVE)
    if not selected:
        return
    info = pm.get_project_change_log(selected)
    if not info:
        messagebox.showinfo("Change Log", "No change log found for this project.")
        return

    # Format the log as a multiline string
    log_str = "\n".join(f"{cid}: {desc}" for cid, desc in info.items())

    # Show in a scrollable popup
    log_popup = tk.Toplevel(root)
    log_popup.title(f"Change Log: {selected}")
    log_popup.geometry("400x300")
    log_popup.grab_set()

    tk.Label(log_popup, text="Change Log", font=("Arial", 12, "bold")).pack(pady=5)

    text_widget = tk.Text(log_popup, wrap=tk.WORD)
    text_widget.insert(tk.END, log_str)
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    scrollbar = tk.Scrollbar(text_widget, command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


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


if __name__ == "__main__":

    # --- Initialize ProjectManager ---
    pm = ProjectManager(index_file=INDEX_FILE, projects_dir=PROJECTS_DIR)

    # --- GUI Setup ---
    root = tk.Tk()
    root.title("Project Manager GUI")

    btn_create = tk.Button(root, text="Create Project", command=create_project)
    btn_create.pack()

    btn_delete = tk.Button(root, text="Delete Project", command=delete_project)
    btn_delete.pack()

    btn_edit = tk.Button(root, text="Edit Project", command=edit)
    btn_edit.pack()

    listbox = tk.Listbox(root)
    listbox.pack(fill=tk.BOTH, expand=True)

    btn_info = tk.Button(root, text="Show Project Info", command=show_project_info)
    btn_info.pack()

    btn_log = tk.Button(root, text="View Change Log", command=get_project_change_log)
    btn_log.pack()

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

