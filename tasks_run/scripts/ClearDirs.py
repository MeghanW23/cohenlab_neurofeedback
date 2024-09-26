import os
import settings
import shutil
import subprocess

def clear_dir(path_to_clear: str):
    print(f"Options for directory: {path_to_clear}: ")
    print("(1) Clear out directory")
    print("(2) Do NOT clear out directory")
    print("(3) Show directory tree ")
    print("(4) Clear element-by-element.")

    while True:
        choice: str = input(f"Input 1, 2, 3, or 4: ")

        if choice == "1":
            print("Ok, clearing out directory now ...")
            try:
                # subprocess.run(["rm", "-rf", f"{path_to_clear}/*"], shell=True)
                print("Done.")
            except Exception as e:
                print(e)
                print("Error clearing dir. Please try clearing manually.")
            break

        elif choice == "2":
            print("Ok, I will not clean out this directory.")
            break

        elif choice == "3":
            print_directory_tree(dir_path=path_to_clear)

        elif choice == "4":
            for element in os.listdir(path_to_clear):
                while True:
                    print(f"Element: {element}")
                    delete_this_file = input("Delete? (y/n): ")
                    if delete_this_file == "y":
                        print("Ok, deleting now .. ")
                        if os.path.isdir(element):
                            try:
                                # subprocess.run(["rm", "-rf", element])
                                print("deleting")
                            except Exception as e:
                                print(e)
                                print("Error clearing dir. Please try clearing manually.")
                        else:
                            try:
                                # subprocess.run(["rm", element])
                                print("deleting")

                            except Exception as e:
                                print(e)
                                print("Error clearing element. Please try clearing manually.")
                        print("deleted file")
                        break
                    elif delete_this_file == "n":
                        print("Ok, not clearing this dir.")
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

    # Prepare the rsync command
    rsync_command = [
        "rsync",
        "-a",
        "--ignore-existing",
        "-e", f"ssh -i {ssh_key}",
        path_to_local,
        f"{remote_host}:{path_to_e3}"
    ]
    """
    # Run the command and suppress output
    try:
        subprocess.run(rsync_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("Files pushed successfully.")
        clear_dir(path_to_clear=path_to_local)

    except subprocess.CalledProcessError as e:
        print(f"Error during push: {e}")
    """

e3_project_dir_path: str = "/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB"

DirectoryDictionary: dict = {}
DirectoryDictionary["just_clear"] = [
    "/workdir/tasks_run/scripts/__pycache__",
    settings.NIFTI_TMP_OUTDIR
]
DirectoryDictionary["push_and_clear"] = [
    (settings.RIFG_LOG_DIR, os.path.join(e3_project_dir_path, "rifg_logs")),
    (settings.SAMBASHARE_DIR_PATH, os.path.join(e3_project_dir_path, "sambashare")),
    (settings.NFB_LOG_DIR, os.path.join(e3_project_dir_path, "nfb_logs")),
    (settings.LOCALIZER_LOG_DIR, os.path.join(e3_project_dir_path, "localizer_data/logs")),
    (settings.ROI_MASK_DIR_PATH, os.path.join(e3_project_dir_path, "localizer_data/subj_space_masks")),
    (settings.MSIT_LOG_DIR, os.path.join(e3_project_dir_path, "msit_logs"))
]

for action in DirectoryDictionary:
    if action == "just_clear":
        for path in DirectoryDictionary["just_clear"]:
            clear_dir(path_to_clear=path)
    if action == "push_and_clear":
        for path_pair in DirectoryDictionary["push_and_clear"]:
            push_to_e3(
                chid=os.environ.get("CHID"),
                path_to_local=path_pair[0],
                path_to_e3=path_pair[1]
            )

print("Script is done.")