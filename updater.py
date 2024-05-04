import os
import sys

import git


repository_path = os.path.dirname(os.path.abspath(__file__))
repo = git.Repo(repository_path)
def update():
    try:
        current = repo.head.commit
        repo.remotes.origin.pull()
        if current != repo.head.commit:
            print("Updated")
            print("Exiting the program...")
            sys.exit()
        print("Already up to date")
    except Exception as e:
        print(f"Error pulling changes: {e}")


