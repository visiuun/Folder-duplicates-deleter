# Duplicate File Finder and Deleter

This Python program helps you find duplicate files in a specified directory and delete them after previewing. It supports various file types, including images and text files, and provides a graphical interface for easy file selection and deletion.

## Features

- **Find Duplicate Files**: Scans the selected directory for duplicate files based on their hash values (SHA-256).
- **Progress Bar**: Displays a progress bar during the scanning process.
- **File Previews**: Shows image previews for image files and text previews for text files, helping you review duplicates before deletion.
- **Selectable Duplicates**: Allows users to select which duplicate files to delete, with a "Select All" option for each group of duplicates.
- **Cross-Platform Notifications**: Sends a desktop notification when the scan is complete.
- **Deletion Confirmation**: Asks for confirmation before deleting selected duplicate files.
- **Windows Beep**: Plays a beep sound on Windows when the scan is finished.

## Requirements

- Python 3.x
- `tkinter` for the graphical user interface
- `Pillow` (PIL) for image previews
- `plyer` for cross-platform notifications
- `winsound` for Windows beep sound
- `concurrent.futures` for parallelizing the file hashing process

To install the required packages, you can run the following commands:

```bash
pip install pillow plyer
```

## Usage

1. Run the script, and it will prompt you to select a folder to scan for duplicates.
2. The program will scan the directory and calculate the hash values of each file.
3. After the scan is complete, a window will appear showing the duplicate files grouped by hash value.
4. You can select individual files to delete or use the "Select All" button to select all duplicates in a group.
5. When you're ready, click the "Delete Selected" button, and the program will confirm the deletion before proceeding.

## How It Works

1. **Hash Calculation**: For each file in the selected directory, the program computes a SHA-256 hash to uniquely identify the file content.
2. **Duplicate Detection**: Files with the same hash value are considered duplicates.
3. **File Deletion**: Once duplicates are identified, you can choose which files to delete, and the program will delete the selected files.
4. **Preview and Selection**: Image files will be displayed as previews, and text files will show a portion of their contents for easier identification.

## Functions

- `calculate_hash(file_path, block_size)`: Computes the SHA-256 hash of a file.
- `find_duplicates(directory, progress, progress_label)`: Scans the directory and identifies duplicate files, updating the progress bar.
- `delete_selected_duplicates(duplicate_dict, selected_files)`: Deletes the selected duplicate files.
- `duplicate_selection_gui(duplicate_dict)`: Displays the duplicate files in a GUI with options to select and delete them.
- `main()`: The main function that initializes the program and starts the duplicate file finding process.
