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
        # Use demo stubs
        demo_commands = {
            "validate": ["python", os.path.join(DEMO_SCRIPTS_DIR, "validate_stub.py")],
            "compliance": ["python", os.path.join(DEMO_SCRIPTS_DIR, "compliance_stub.py")],
            "boundary": ["python", os.path.join(DEMO_SCRIPTS_DIR, "validate_stub.py")],
            "discover": ["echo", "Demo: Tool discovery not implemented"],
            "status": ["echo", "Demo: Status check OK"],
        }
        cmd = demo_commands.get(request.tool_id)
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
        }

        # Fallback: direct script execution (if make/uv not available)
        tool_direct_commands = {
            "validate": [sys.executable, "AgentQMS/agent_tools/compliance/validate_artifacts.py", "--all"],
            "compliance": [sys.executable, "AgentQMS/agent_tools/compliance/monitor_artifacts.py", "--check"],
            "boundary": [sys.executable, "AgentQMS/agent_tools/compliance/validate_boundaries.py"],
            "discover": [sys.executable, "AgentQMS/agent_tools/core/discover.py"],
            "status": ["echo", "Status check - AgentQMS interface available"],
        }

        if request.tool_id not in tool_make_commands:
            return {
                "success": False,
                "error": f"Unknown tool: {request.tool_id}",
                "output": ""
            }

        try:
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
