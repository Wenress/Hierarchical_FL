import subprocess
import os

def run_shell_script(script_path, server_ip: str):

    try:
        # Ensure the script exists
        if not os.path.exists(script_path):
            # print current working directory
            raise FileNotFoundError(f"Script {script_path} does not exist.")
        result = subprocess.run(["sh", script_path, server_ip], check=True, text=True, capture_output=True)
        #result = subprocess.run(["ls", "-l", "./utils"], check=True, text=True, capture_output=True)
        if result.stdout:
            print(f"[OUTPUT] {result.stdout}")


    except subprocess.CalledProcessError as e:
        print(f"[ERROR]: {e}")