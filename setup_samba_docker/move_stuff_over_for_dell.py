import os
import shutil
import time
import subprocess

def copy_directory(input_directory: str, output_directory: str, username):     

    # Iterate through each item in the inputted directory
    for path_name in os.listdir(input_directory):

        full_path: str = os.path.join(input_directory, path_name) # Get the full source path

        # If the full path is a directory
        if os.path.isdir(full_path):

            # Make a directory in the output directory with the same name
            new_output_dir: str = os.path.join(output_directory, path_name)

            # create dir if it doesnt exist 
            if not os.path.exists(new_output_dir): 

                # os.makedirs(new_output_dir, exist_ok=True)
                subprocess.run([
                    "ssh", "mac", "mkdir", "-p", new_output_dir
                ])
            
            # Recursively copy every file in the input directory to the new output directory
            copy_directory(input_directory=full_path, output_directory=new_output_dir, username=copy_directory)

        else:

            # Copy each non-directory file into the given output directory if it exists 
            new_file_path = os.path.join(output_directory, path_name)

            if not os.path.exists(new_file_path):

                # shutil.copy(full_path, output_directory)
            
                subprocess.run([
                        "scp", full_path, f"mac:{output_directory}"
                    ])


def get_number_of_elements(input_directory: str, number_of_elements: int = 0) -> int:

    # for each file/dir ect in os.listdir
    for element in os.listdir(input_directory): 

        # count the element 
        number_of_elements += 1

        # recursively count every file in the input directory
        if os.path.isdir(os.path.join(input_directory, element)):
            
            number_of_elements = get_number_of_elements(input_directory=os.path.join(input_directory, element), number_of_elements=number_of_elements)

    return number_of_elements

# --- define and check directories ---

username = "meghan"

input_directory: str = "/home/rt/sambashare" # input directory 

output_directory: str = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/sambashare/" # output directory 

if not os.path.exists(input_directory): raise FileNotFoundError(f"Could not find inputted path for input_directory: {input_directory}")



# --- start copying and checking sequence  ---

copy_directory(input_directory=input_directory,output_directory=output_directory, username=username) # copy everything to start 

starting_number_of_elements = get_number_of_elements(input_directory=input_directory)

while True:
    
    current_number_of_elements = get_number_of_elements(input_directory=input_directory)

    if starting_number_of_elements != current_number_of_elements:

        starting_number_of_elements = current_number_of_elements

        copy_directory(input_directory=input_directory,output_directory=output_directory, username=username)

    else:
        time.sleep(0.1)