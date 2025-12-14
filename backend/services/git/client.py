import subprocess
import os
from typing import Optional

class GitClient:
    """
    A simple wrapper around local git commands to ensure safety during auto-remediation.
    """
    
    @staticmethod
    def is_git_repo(path: str) -> bool:
        return os.path.exists(os.path.join(path, ".git"))

    @staticmethod
    def commit_file(file_path: str, message: str, project_root: str = None) -> bool:
        """
        Stages and commits a single file.
        Returns True if successful, False otherwise.
        """
        if not project_root:
            # Assume we are running from backend/ and project root is parent
            # But better to rely on passed root or CWD if configured correctly
             project_root = os.getcwd()

        try:
            # 1. Stage the file
            subprocess.run(
                ["git", "add", file_path], 
                cwd=project_root, 
                check=True,
                capture_output=True
            )

            # 2. Commit
            # Using -m with a specific message
            subprocess.run(
                ["git", "commit", "-m", f"AgentQMS Auto-Fix: {message}", file_path],
                cwd=project_root,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e.stderr.decode()}")
            return False
        except Exception as e:
            print(f"Git operation error: {str(e)}")
            return False

    @staticmethod
    def get_last_commit(file_path: str, project_root: str = None) -> Optional[str]:
        if not project_root:
             project_root = os.getcwd()
        
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H - %s (%cd)", file_path],
                cwd=project_root,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception:
            return None
