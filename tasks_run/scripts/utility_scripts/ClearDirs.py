import os
import shutil
import subprocess
import glob
import sys

sys.path.insert(1, "/workdir/tasks_run/scripts/")
import settings

files_to_keep = {".DS_Store", ".gitkeep", ".gitignore", "scores"}
def clear_dir(path_to_clear: str):
    print("-------------------------------------------")
    print(f"CLEAR Options for directory: {path_to_clear}: ")
    print("-------------------------------------------")
    print("(1) Clear out directory")
    print("(2) Do NOT clear out directory")
    print("(3) Show directory tree ")
    print("(4) Clear element-by-element.")

    while True:
        choice: str = input(f"Input 1, 2, 3, or 4: ")

        if choice == "1":
            print("Ok, clearing out directory now ...")
            try:
                # Use glob to match all files and directories in path_to_clear
                for item in glob.glob(os.path.join(path_to_clear, '*')):
                    global files_to_keep
                    if os.path.basename(item) in files_to_keep:
                        # do not remove git files as having a completely clear directory will prevent it from being pushed to git
                        print(f"Keeping file: {os.path.basename(item)}")
                        pass
                    elif os.path.isdir(item):
                        shutil.rmtree(item)
                    else:
                        os.remove(item)
                print(f"Cleared contents of {path_to_clear}")
            except Exception as e:
                print(f"Error clearing directory: {e}")

            break

        elif choice == "2":
            print("Ok, I will not clean out this directory.")
            break

        elif choice == "3":
            print_directory_tree(dir_path=path_to_clear)

        elif choice == "4":
            for element in os.listdir(path_to_clear):
                while True:
                    if "gitkeep" in element:
                        break
                    print(f"Element: {element}")
                    delete_this_file = input("Delete? (y/n): ")
                    if delete_this_file == "y":
                        print("Ok, deleting now .. ")
                        if os.path.isdir(os.path.join(path_to_clear, element)):
                            try:
                                shutil.rmtree(element)
                            except Exception as e:
                                print("ERROR: ")
                                print(e)
                                print("Error clearing dir. Please try clearing manually.")
                        else:
                            try:
                                os.remove(os.path.join(path_to_clear, element))

                            except Exception as e:
                                print("ERROR: ")
                                print(e)
                                print("Error clearing element. Please try clearing manually.")
                        print("deleted file")
                        break
                    elif delete_this_file == "n":
                        print("Ok, not clearing this element.")
                        break
                    else:
                        print("Please choose either 1 or 2")

            break

        else:
            print("Please choose 1, 2, or 3.")
def print_directory_tree(dir_path: str, indent=""):
    # Check if directory exists
    if not os.path.exists(dir_path):
        print(f"Directory '{dir_path}' does not exist.")
        return

    # List all files and directories
    items = os.listdir(dir_path)
    items.sort()

    for index, item in enumerate(items):
        item_path = os.path.join(dir_path, item)
        # Print the current item
        is_last = index == len(items) - 1
        prefix = "└── " if is_last else "├── "
        print(indent + prefix + item)

        # If it's a directory, recursively print its contents
        if os.path.isdir(item_path):
            # Increase the indent for sub-items
            new_indent = indent + ("    " if is_last else "│   ")
            print_directory_tree(item_path, new_indent)
def push_to_e3(chid, path_to_local, path_to_e3):
    ssh_key = f"/workdir/.ssh/docker_e3_key_{chid}"
    remote_host = f"{chid}@e3-login.tch.harvard.edu"

    # Ensure path_to_local ends with a slash to push contents, not the directory itself
    if not path_to_local.endswith("/"):
        path_to_local = f"{path_to_local}/"

    # Prepare the rsync command
    rsync_command = [
        "rsync",
        "-a",
        "--ignore-existing",
        "-e", f"ssh -i {ssh_key}",
        path_to_local,
        f"{remote_host}:{path_to_e3}"
    ]
    # Run the command and suppress output
    try:
        subprocess.run(rsync_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("Files pushed successfully.")
        clear_dir(path_to_clear=path_to_local)

    except subprocess.CalledProcessError as e:
        print(f"Error during push: {e}")
def check_if_empty_already(path_to_clear: str) -> bool:
    global files_to_keep

    # List all files in the directory
    files_in_directory = set(os.listdir(path_to_clear))

    # Check if all files in the directory are part of files_to_keep
    if files_in_directory.issubset(files_to_keep):
        return True
    return False

e3_project_dir_path: str = "/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB"

DirectoryDictionary: dict = {}
DirectoryDictionary["just_clear"] = [
    "/workdir/tasks_run/scripts/__pycache__",
    settings.TMP_OUTDIR_PATH
]
DirectoryDictionary["push_and_clear"] = [
    (settings.RIFG_LOG_DIR, settings.E3_PATH_TO_RIFG_LOGS),
    (settings.SAMBASHARE_DIR_PATH, settings.E3_PATH_TO_SAMBASHARE),
    (settings.NFB_LOG_DIR, settings.E3_PATH_TO_NFB_LOGS),
    (settings.LOCALIZER_LOG_DIR, settings.E3_PATH_TO_LOCALIZER_DATA_LOGS),
    (settings.ROI_MASK_DIR_PATH, settings.E3_PATH_TO_SUBJECT_SPACE_MASKS),
    (settings.MSIT_LOG_DIR, settings.E3_PATH_TO_MSIT_LOGS)
]

for action in DirectoryDictionary:
    print(f"Running paths in list: {action} ")
    if action == "just_clear":
        for path in DirectoryDictionary["just_clear"]:
            if check_if_empty_already(path_to_clear=path):
                print(f"Skipping empty dir: {path} ... ")
            else:
                clear_dir(path_to_clear=path)
    if action == "push_and_clear":
        for path_pair in DirectoryDictionary["push_and_clear"]:
            if check_if_empty_already(path_to_clear=path_pair[0]):
                print(f"Skipping empty dir: {path_pair[0]} ... ")
                continue
            print("-------------------------------------------")
            print(f"PUSH Options for directory: {path_pair[0]}: ")
            print("-------------------------------------------")
            print("(y) Yes, push the directory elements to their associated path on e3. ")
            print("(n) No, do not push the directory elements to their associated path on e3.")

            while True:
                push_choice = input("Please type either 'y' or 'n': ")
                if push_choice == "y":
                    print("Ok, pushing to e3 ...")
                    push_to_e3(
                        chid=os.environ.get("CHID"),
                        path_to_local=path_pair[0],
                        path_to_e3=path_pair[1]
                    )
                    break

                elif push_choice == "n":
                    print("Ok, I will not push this directory to E3. ")
                    break

                else:
                    print("Not a valid option.")

print("Script is done.")