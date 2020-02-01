import os


def get_model_file_path(model_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return f"{current_dir}/{model_name}"
