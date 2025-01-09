import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import defaultdict
from PIL import Image, ImageTk
import winsound  # For Windows beep sound
from plyer import notification  # For cross-platform notification
from concurrent.futures import ThreadPoolExecutor

# Function to calculate file hash (SHA-256)
def calculate_hash(file_path, block_size=65536):
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as file:
            for block in iter(lambda: file.read(block_size), b''):
                hasher.update(block)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    return hasher.hexdigest()

# Function to find duplicate files in the selected directory with a progress bar
def find_duplicates(directory, progress, progress_label):
    hash_map = defaultdict(list)
    total_files = sum(len(files) for _, _, files in os.walk(directory))
    current_file = 0
    
    # Using ThreadPoolExecutor to parallelize the file hashing
    with ThreadPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                futures.append(executor.submit(process_file, file_path, hash_map))
        
        # Update progress as files are processed
        for future in futures:
            file_hash, file_path = future.result()
            if file_hash:
                hash_map[file_hash].append(file_path)
            current_file += 1
            progress['value'] = (current_file / total_files) * 100
            progress_label.config(text=f"Scanning {current_file}/{total_files} files...")
            progress.update()

    duplicates = {k: v for k, v in hash_map.items() if len(v) > 1}
    return duplicates

# Helper function for submitting individual files to the executor
def process_file(file_path, hash_map):
    file_hash = calculate_hash(file_path)
    return file_hash, file_path

# Function to delete selected duplicates
def delete_selected_duplicates(duplicate_dict, selected_files):
    for hash_val, files in duplicate_dict.items():
        for file in files[1:]:  # Skip the first file in each duplicate group
            if file in selected_files:
                try:
                    os.remove(file)
                    print(f"Deleted: {file}")
                except Exception as e:
                    print(f"Error deleting {file}: {e}")

# GUI for duplicate selection with side-by-side preview and "Select All" option
def duplicate_selection_gui(duplicate_dict):
    selection_window = tk.Toplevel()
    selection_window.title("Select Duplicates to Delete")
    selection_window.geometry("1000x600")

    selected_files = []

    # Canvas and Scrollbar for the list of duplicates
    canvas = tk.Canvas(selection_window)
    scrollbar = ttk.Scrollbar(selection_window, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Preview frame for displaying selected file content
    preview_frame = tk.Frame(selection_window, width=400, height=500)
    preview_frame.pack(side="right", padx=10, pady=10)

    preview_label = tk.Label(preview_frame, text="File Preview", font=("Arial", 14))
    preview_label.pack(pady=5)
    preview_canvas = tk.Canvas(preview_frame, width=380, height=380, bg="white")
    preview_canvas.pack()

    def show_preview(file_path):
        preview_canvas.delete("all")
        try:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Display image preview
                img = Image.open(file_path)
                img.thumbnail((380, 380))
                img_tk = ImageTk.PhotoImage(img)
                preview_canvas.create_image(190, 190, image=img_tk)
                preview_canvas.image = img_tk
            elif file_path.lower().endswith('.txt'):
                # Display text file preview
                with open(file_path, 'r') as file:
                    text_content = file.read(500)  # Preview only first 500 characters
                preview_canvas.create_text(190, 190, text=text_content, anchor="center", width=360)
            else:
                preview_canvas.create_text(190, 190, text="No preview available", anchor="center")
        except Exception as e:
            print(f"Error loading preview for {file_path}: {e}")
            preview_canvas.create_text(190, 190, text="Error loading preview", anchor="center")

    # Add a dictionary to hold variables for checkboxes
    file_vars = {}

    # Group selection checkboxes and preview
    for hash_val, files in duplicate_dict.items():
        # Frame for each duplicate group
        group_frame = ttk.LabelFrame(scroll_frame, text=f"Duplicate Group (hash: {hash_val[:10]}...)", padding=5)
        group_frame.pack(fill="x", padx=5, pady=5)

        # "Select All" checkbox for the current group (excluding the original)
        select_all_var = tk.BooleanVar()
        select_all_chk = tk.Checkbutton(group_frame, text="Select All (excluding original)", variable=select_all_var)
        select_all_chk.grid(row=0, column=0, sticky="w")

        # Function to toggle all checkboxes in the group, excluding the original file
        def toggle_all_in_group(var, file_vars, files):
            select_all_value = var.get()  # Get the value of the "Select All" checkbox
            for i, file in enumerate(files[1:]):  # Skip the first file (original)
                if file in file_vars:
                    file_vars[file].set(select_all_value)  # Set the value of the checkbox

        # Create checkboxes for each duplicate (excluding the original)
        for i, file in enumerate(files):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(group_frame, text=file, variable=var, onvalue=True, offvalue=False)
            chk.grid(row=i+1, column=0, sticky="w")
            chk.bind("<Enter>", lambda e, f=file: show_preview(f))  # Show preview on hover
            file_vars[file] = var

        # Link the "Select All" checkbox to toggle all files in the group
        select_all_var.trace_add("write", lambda *args, var=select_all_var, file_vars=file_vars, files=files: toggle_all_in_group(var, file_vars, files))

    # Scrollbar and canvas packing
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Button to select or deselect all duplicate groups
    def toggle_select_all_duplicate_groups():
        select_all = select_all_button.config('text')[-1] == "Select All Duplicate Groups"
        
        # Iterate through all duplicate groups and toggle checkboxes
        for hash_val, files in duplicate_dict.items():
            for i, file in enumerate(files[1:]):  # Skip the first file (original)
                var = file_vars.get(file)
                if var:
                    var.set(select_all)  # Set the value of the checkbox to select/deselect all

        # Update the button text based on the state
        if select_all:
            select_all_button.config(text="Deselect All Duplicate Groups")
        else:
            select_all_button.config(text="Select All Duplicate Groups")

    # Confirm deletion button
    def confirm_deletion():
        files_to_delete = [file for file, var in file_vars.items() if var.get()]
        
        # Display confirmation dialog before deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(files_to_delete)} selected duplicate files?"):
            delete_selected_duplicates(duplicate_dict, files_to_delete)
            selection_window.destroy()

    confirm_button = tk.Button(selection_window, text="Delete Selected", command=confirm_deletion)
    confirm_button.pack()

    # Play a beep when the scanning is done
    winsound.Beep(1000, 500)  # Frequency 1000Hz, duration 500ms
    # Alternatively, notify completion with a system notification
    notification.notify(
        title='Scan Complete',
        message='Duplicate file scan is complete.',
        timeout=10  # Time in seconds for the notification to stay visible
    )

    # Button to toggle select/deselect all duplicate groups
    select_all_button = tk.Button(selection_window, text="Select All Duplicate Groups", command=toggle_select_all_duplicate_groups)
    select_all_button.pack(pady=10)

# Main function to select folder and find/delete duplicates
def main():
    root = tk.Tk()
    root.withdraw()

    # Select directory
    directory = filedialog.askdirectory(title="Select Folder to Search for Duplicates")
    if not directory:
        print("No directory selected.")
        return

    # Progress window setup
    progress_window = tk.Toplevel(root)
    progress_window.title("Scanning for Duplicates")
    progress_label = tk.Label(progress_window, text="Starting scan...")
    progress_label.pack(pady=10)
    progress = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    # Find duplicates with progress bar
    duplicates = find_duplicates(directory, progress, progress_label)
    progress_window.destroy()

    if not duplicates:
        messagebox.showinfo("No Duplicates", "No duplicate files found in the selected folder.")
        print("No duplicate files found.")
        return

    # Show duplicates in graphical selection window
    duplicate_selection_gui(duplicates)
    root.mainloop()

if __name__ == "__main__":
    main()