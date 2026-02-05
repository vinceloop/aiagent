import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=None):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        valid_file_path = os.path.commonpath([abs_working_dir, abs_file_path]) == abs_working_dir

        if not valid_file_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(abs_file_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not abs_file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", abs_file_path]
        if args:
            command.extend(args)
        cp = subprocess.run(command, cwd=abs_working_dir, capture_output=True, text=True, timeout=30)

        output = []
        if cp.returncode != 0:
            output.append(f"Process exited with code {cp.returncode}")
        if not cp.stdout and not cp.stderr:
            output.append("No output produced")
        if cp.stdout:
            output.append(f"STDOUT:\n{cp.stdout}")
        if cp.stderr:
            output.append(f"STDERR:\n{cp.stderr}")
        
        return "\n".join(output)

    except Exception as e:
        return f"Error: executing Python file: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a specified Python file within the working directory and returns its output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to run, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="Optional list of arguments to pass to the Python script",
            ),
        },
        required=["file_path"],
    ),
)
