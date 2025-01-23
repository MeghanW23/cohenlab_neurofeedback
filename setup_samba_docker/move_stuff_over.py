import os
import shutil
import time

def copy_directory(input_directory: str, output_directory: str):     

    # Iterate through each item in the inputted directory
    for path_name in os.listdir(input_directory):

        full_path: str = os.path.join(input_directory, path_name) # Get the full source path

        # If the full path is a directory
        if os.path.isdir(full_path):

            # Make a directory in the output directory with the same name
            new_output_dir: str = os.path.join(output_directory, path_name)

            # create dir if it doesnt exist 
            if not os.path.exists(new_output_dir): 

                os.makedirs(new_output_dir, exist_ok=True)
            
            # Recursively copy every file in the input directory to the new output directory
            copy_directory(input_directory=full_path, output_directory=new_output_dir)

        else:

            # Copy each non-directory file into the given output directory if it exists 
            new_file_path = os.path.join(output_directory, path_name)

            if not os.path.exists(new_file_path):

                shutil.copy(full_path, output_directory)


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

sambashare_directory: str = "/sambashare" # input directory 

mounted_directory: str = "/samba_mount_to_mac" # output directory 

if not os.path.exists(sambashare_directory): raise FileNotFoundError(f"Could not find inputted path for sambashare_directory: {sambashare_directory}")

if not os.path.exists(mounted_directory): raise FileNotFoundError(f"Could not find inputted path for mounted_directory: {mounted_directory}")


# --- start copying and checking sequence  ---

copy_directory(input_directory=sambashare_directory,output_directory=mounted_directory) # copy everything to start 

starting_number_of_elements = get_number_of_elements(input_directory=sambashare_directory)

while True:
    
    current_number_of_elements = get_number_of_elements(input_directory=sambashare_directory)

    if starting_number_of_elements != current_number_of_elements:

        starting_number_of_elements = current_number_of_elements

        copy_directory(input_directory=sambashare_directory,output_directory=mounted_directory)

    else:
        time.sleep(0.1)