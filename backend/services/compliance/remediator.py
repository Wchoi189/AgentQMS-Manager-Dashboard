
import os
import frontmatter
from datetime import datetime
from services.compliance.validator import Validator
from services.git.client import GitClient

class Remediator:
    def __init__(self):
        self.validator = Validator()
        self.git = GitClient()

    def fix_violation(self, file_path: str, rule_id: str, dry_run: bool = False) -> dict:
        """
        Attempts to fix a specific violation in a file.
        Returns result dict with status and message.
        """
        if not os.path.exists(file_path):
             return {"success": False, "message": "File not found"}

        try:
            # Load the file
            post = frontmatter.load(file_path)
            
            # Apply Fix based on rule_id
            changed = False
            fix_message = ""

            if rule_id == "missing_required_field":
                 # We need to know WHICH field is missing. 
                 # Since we only get rule_id, we infer common missing fields or check generic ones.
                 # For Phase 3 L1, we focus on 'date', 'status', 'category'.
                 
                 # 1. Date
                 if "date" not in post.metadata:
                     post.metadata["date"] = datetime.now().strftime("%Y-%m-%d %H:%M (KST)")
                     changed = True
                     fix_message = "Added missing date"
                 
                 # 2. Status
                 elif "status" not in post.metadata:
                     # Default status based on type? Or just 'draft'
                     post.metadata["status"] = "draft"
                     changed = True
                     fix_message = "Added missing status (draft)"

                 # 3. Category
                 elif "category" not in post.metadata:
                     post.metadata["category"] = "uncategorized"
                     changed = True
                     fix_message = "Added missing category"
                 
                 # 4. Tags
                 elif "tags" not in post.metadata:
                     post.metadata["tags"] = []
                     changed = True
                     fix_message = "Added missing tags"

            elif rule_id == "invalid_status":
                # Reset to draft if invalid
                post.metadata["status"] = "draft"
                changed = True
                fix_message = "Reset invalid status to 'draft'"

            if not changed:
                 return {"success": False, "message": f"No automatic fix available for rule '{rule_id}' or field was already present."}

            if dry_run:
                # Return diff logic
                import difflib
                
                # We need the original content as string
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                # Get new content as string
                new_content = frontmatter.dumps(post)
                
                # Generate diff
                diff = difflib.unified_diff(
                    original_content.splitlines(),
                    new_content.splitlines(),
                    fromfile="original",
                    tofile="fixed",
                    lineterm=""
                )
                
                return {
                    "success": True,
                    "message": f"Dry Run: {fix_message}",
                    "dry_run": True,
                    "diff": "\n".join(list(diff)),
                    "new_content": new_content
                }

            # Save the file
            with open(file_path, "wb") as f:
                frontmatter.dump(post, f)

            # Auto-Commit
            commit_success = self.git.commit_file(file_path, fix_message)
            
            return {
                "success": True, 
                "message": f"Fixed: {fix_message}",
                "git_committed": commit_success
            }

        except Exception as e:
            return {"success": False, "message": f"Error applying fix: {str(e)}"}
