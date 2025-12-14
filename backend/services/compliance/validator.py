import os
import yaml
import frontmatter
from typing import List, Dict, Any
from pydantic import ValidationError

from services.compliance.models import ArtifactMetadata, ValidationReport, ValidationViolation

# Load Rules
RULES_PATH = os.path.join(os.path.dirname(__file__), "rules.yaml")
with open(RULES_PATH, "r") as f:
    RULES = yaml.safe_load(f)

class Validator:
    def __init__(self):
        self.rules = RULES

    def validate_file(self, file_path: str) -> ValidationReport:
        violations = []
        metadata_dict = {}

        if not os.path.exists(file_path):
            return ValidationReport(
                file_path=file_path, 
                is_compliant=False, 
                violations=[ValidationViolation(rule_id="file_not_found", message="File does not exist")]
            )

        try:
            post = frontmatter.load(file_path)
            metadata_dict = post.metadata
            
            # 1. Pydantic Base Validation (Type Checks)
            try:
                # We normalize metadata keys to lowercase for Pydantic if needed, but standard is lowercase
                ArtifactMetadata(**metadata_dict)
            except ValidationError as e:
                for error in e.errors():
                    field = error["loc"][0] if error["loc"] else "unknown"
                    msg = error["msg"]
                    violations.append(ValidationViolation(
                        rule_id="schema_validation",
                        message=f"Field '{field}': {msg}",
                        field=str(field)
                    ))

            # 2. Rule-Based Validation (Logic Checks)
            artifact_type = metadata_dict.get("type")
            
            # Check Common Required Fields (redundant with Pydantic but good for specific error messages)
            for field in self.rules["common"]["required_fields"]:
                if field not in metadata_dict:
                    violations.append(ValidationViolation(
                        rule_id="missing_required_field",
                        message=f"Missing required field: {field}",
                        field=field
                    ))

            # Type-Specific Rules
            if artifact_type and artifact_type in self.rules["artifact_types"]:
                type_rules = self.rules["artifact_types"][artifact_type]
                
                # Required Fields
                for field in type_rules.get("required_fields", []):
                    if field not in metadata_dict:
                        violations.append(ValidationViolation(
                            rule_id="missing_required_field", 
                            message=f"Missing required field for type '{artifact_type}': {field}",
                            field=field
                        ))
                
                # Allowed Statuses
                if "allowed_statuses" in type_rules:
                    status = metadata_dict.get("status")
                    if status and status not in type_rules["allowed_statuses"]:
                        violations.append(ValidationViolation(
                            rule_id="invalid_status",
                            message=f"Status '{status}' not allowed for type '{artifact_type}'. Allowed: {type_rules['allowed_statuses']}",
                            field="status"
                        ))

        except Exception as e:
            violations.append(ValidationViolation(
                rule_id="parse_error",
                message=f"Failed to parse file: {str(e)}"
            ))

        return ValidationReport(
            file_path=file_path,
            is_compliant=len(violations) == 0,
            violations=violations,
            metadata=metadata_dict
        )

    def validate_directory(self, dir_path: str) -> Dict[str, Any]:
        """Validate all markdown files in a directory recursively."""
        reports = []
        total_files = 0
        valid_files = 0
        violations_list = []

        import glob
        search_pattern = os.path.join(dir_path, "**", "*.md")
        files = glob.glob(search_pattern, recursive=True)

        for f in files:
            report = self.validate_file(f)
            reports.append(report)
            total_files += 1
            if report.is_compliant:
                valid_files += 1
            else:
                for v in report.violations:
                    violations_list.append({
                        "file": os.path.basename(f),
                        "path": f,
                        "rule_id": v.rule_id,
                        "message": v.message,
                        "severity": v.severity
                    })

        compliance_rate = (valid_files / total_files) * 100 if total_files > 0 else 100

        return {
            "compliance_rate": compliance_rate,
            "total_files": total_files,
            "valid_files": valid_files,
            "violations": violations_list
        }
