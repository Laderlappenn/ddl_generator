import subprocess
import os

repository_path = os.path.dirname(os.path.abspath(__file__))
def update():
    try:
        subprocess.run(['git', '-C', repository_path, 'pull'])
        return True, "Changes pulled successfully."
    except Exception as e:
        return False, f"Error pulling changes: {e}"


