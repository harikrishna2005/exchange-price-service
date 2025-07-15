import os

# Get the parent directory of 'src' (which is the project root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print(project_root)
os.environ["PYTHONPATH"] = project_root
