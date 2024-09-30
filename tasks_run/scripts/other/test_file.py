import os
def get_elements(input_path):
    for element in os.listdir(input_path):
        full_path = os.path.join(input_path, element)

        if full_path == input_path:
            pass

        elif os.path.isdir(full_path):
            print(f"directory: {full_path}")
            get_elements(full_path)
        else:
            print(f"file: {full_path}")

get_elements(input_path="/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB/")