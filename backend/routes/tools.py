"""Tools execution endpoint."""
import os
import subprocess
import sys

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])

# Check if running in demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
DEMO_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../demo_scripts")
)


class ToolExecRequest(BaseModel):
    tool_id: str
    args: dict


@router.post("/exec")
async def execute_tool(request: ToolExecRequest):
    """Execute an AgentQMS tool via make command or demo stub."""
    
    if DEMO_MODE:
        # Check if tool_id is a script path
        if request.tool_id.startswith(("AgentQMS/", "agent_tools/", "AgentQMS\\", "agent_tools\\")):
            script_path = os.path.join(workspace_root, request.tool_id.replace("\\", "/"))
            if os.path.exists(script_path):
                cmd = [sys.executable, script_path]
                if request.args:
                    for key, value in request.args.items():
                        if value:
                            cmd.append(str(value))
            else:
                return {
                    "success": False,
                    "error": f"Script not found: {script_path}",
                    "output": ""
                }
        else:
            # Use demo stubs
            demo_commands = {
                "validate": ["python", os.path.join(DEMO_SCRIPTS_DIR, "validate_stub.py")],
                "compliance": ["python", os.path.join(DEMO_SCRIPTS_DIR, "compliance_stub.py")],
                "boundary": ["python", os.path.join(DEMO_SCRIPTS_DIR, "validate_stub.py")],
                "discover": ["echo", "Demo: Tool discovery not implemented"],
                "status": ["echo", "Demo: Status check OK"],
                "ast_analyze": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "analyze", "."],
                "ast_generate_tests": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "generate-tests"],
                "ast_extract_docs": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "extract-docs"],
                "ast_check_quality": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "check-quality", "."],
            }
            cmd = demo_commands.get(request.tool_id)
            
            # For AST tools in demo mode, add arguments
            if cmd and request.tool_id.startswith("ast_") and request.args:
                for key, value in request.args.items():
                    if value:
                        cmd.append(str(value))
        
        if not cmd:
            return {
                "success": False,
                "error": f"Unknown tool: {request.tool_id}",
                "output": ""
            }
        
        # Get workspace root for demo scripts
        workspace_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..")
        )
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=workspace_root
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Tool execution timed out",
                "output": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": ""
            }
    else:
        # Real execution path (expects AgentQMS present)
        # Workspace root (backend/routes -> backend -> project root)
        workspace_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..")
        )

        # Verify AgentQMS exists
        agentqms_path = os.path.join(workspace_root, "AgentQMS", "interface")
        if not os.path.exists(agentqms_path):
            return {
                "success": False,
                "error": f"AgentQMS path not found at {agentqms_path}",
                "output": ""
            }

        # Map tool IDs to commands (try make first, fallback to direct script execution)
        tool_make_commands = {
            "validate": ["make", "-C", "AgentQMS/interface", "validate"],
            "compliance": ["make", "-C", "AgentQMS/interface", "compliance"],
            "boundary": ["make", "-C", "AgentQMS/interface", "boundary"],
            "discover": ["make", "-C", "AgentQMS/interface", "discover"],
            "status": ["make", "-C", "AgentQMS/interface", "status"],
            "ast_analyze": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "analyze"],
            "ast_generate_tests": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "generate-tests"],
            "ast_extract_docs": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "extract-docs"],
            "ast_check_quality": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "check-quality"],
        }

        # Fallback: direct script execution (if make/uv not available)
        # Auto-detect artifacts root for validation tools
        def get_artifacts_root_for_tools():
            """Get artifacts root with auto-detection."""
            demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
            artifacts_rel = "demo_data/artifacts" if demo_mode else "docs/artifacts"
            artifacts_root = os.path.join(workspace_root, artifacts_rel)
            
            # Auto-detect: if configured path doesn't exist, try the alternative
            if not os.path.exists(artifacts_root):
                alt_artifacts_rel = "docs/artifacts" if demo_mode else "demo_data/artifacts"
                alt_artifacts_root = os.path.join(workspace_root, alt_artifacts_rel)
                if os.path.exists(alt_artifacts_root):
                    return alt_artifacts_root
            return artifacts_root
        
        artifacts_root = get_artifacts_root_for_tools()
        
        tool_direct_commands = {
            "validate": [sys.executable, "AgentQMS/agent_tools/compliance/validate_artifacts.py", "--all", "--artifacts-root", artifacts_root],
            "compliance": [sys.executable, "AgentQMS/agent_tools/compliance/monitor_artifacts.py", "--check", "--artifacts-root", artifacts_root],
            "boundary": [sys.executable, "AgentQMS/agent_tools/compliance/validate_boundaries.py"],
            "discover": [sys.executable, "AgentQMS/agent_tools/core/discover.py"],
            "status": ["echo", "Status check - AgentQMS interface available"],
            "ast_analyze": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "analyze"],
            "ast_generate_tests": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "generate-tests"],
            "ast_extract_docs": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "extract-docs"],
            "ast_check_quality": [sys.executable, "AgentQMS/interface/cli_tools/ast_analysis.py", "check-quality"],
        }

        # Check if tool_id is a script path (starts with AgentQMS/ or agent_tools/)
        if request.tool_id.startswith(("AgentQMS/", "agent_tools/", "AgentQMS\\", "agent_tools\\")):
            # Direct script execution
            script_path = os.path.join(workspace_root, request.tool_id.replace("\\", "/"))
            if not os.path.exists(script_path):
                return {
                    "success": False,
                    "error": f"Script not found: {script_path}",
                    "output": ""
                }
            
            # Build command with arguments
            cmd = [sys.executable, script_path]
            if request.args:
                for key, value in request.args.items():
                    if value:  # Only add non-empty arguments
                        cmd.append(str(value))
            
            # Set PYTHONPATH for imports
            env = os.environ.copy()
            env["PYTHONPATH"] = workspace_root + os.pathsep + env.get("PYTHONPATH", "")
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=workspace_root,
                    env=env
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                    "return_code": result.returncode
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "Tool execution timed out",
                    "output": ""
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "output": ""
                }
        
        if request.tool_id not in tool_make_commands:
            return {
                "success": False,
                "error": f"Unknown tool: {request.tool_id}",
                "output": ""
            }

        try:
            # For AST tools, use direct execution (they don't use make)
            if request.tool_id.startswith("ast_"):
                cmd = tool_direct_commands.get(request.tool_id, tool_make_commands[request.tool_id])
                # Add arguments from request.args (AST tools use positional args)
                if request.args:
                    # For AST tools, 'path' key contains the positional argument
                    if 'path' in request.args and request.args['path']:
                        cmd.append(str(request.args['path']))
                    # Also check for direct values (fallback)
                    for key, value in request.args.items():
                        if key != 'path' and value:  # Skip 'path' as we already handled it
                            cmd.append(str(value))
                
                # Set PYTHONPATH for imports
                env = os.environ.copy()
                env["PYTHONPATH"] = workspace_root + os.pathsep + env.get("PYTHONPATH", "")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=workspace_root,
                    env=env
                )
            else:
                # Try make command first
                cmd = tool_make_commands[request.tool_id]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=workspace_root
                )

                # If make fails and it's a known tool, try direct script execution
                if result.returncode != 0 and request.tool_id in tool_direct_commands:
                    fallback_cmd = tool_direct_commands[request.tool_id]
                    # Set PYTHONPATH for imports
                    env = os.environ.copy()
                    env["PYTHONPATH"] = workspace_root + os.pathsep + env.get("PYTHONPATH", "")
                    
                    result = subprocess.run(
                        fallback_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=workspace_root,
                        env=env
                    )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Tool execution timed out",
                "output": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": ""
            }
