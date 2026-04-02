from __future__ import annotations

import subprocess
from pathlib import Path

from deepagents import create_deep_agent
from app.core.llm_factory import get_llm


BASE_DIR = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = BASE_DIR / "generated_tests"
OUTPUT_DIR.mkdir(exist_ok=True)
 
 
def save_test_script(filename: str, content: str) -> str:
    """
    Save a generated pytest script into generated_tests/.
    Returns the full saved path.
    """
    safe_name = Path(filename).name
 
    if not safe_name:
        safe_name = "test_generated.py"
 
    if not safe_name.endswith(".py"):
        safe_name += ".py"
 
    path = OUTPUT_DIR / safe_name
    path.write_text(content, encoding="utf-8")
    return str(path)
 
 
def read_test_script(filename: str) -> str:
    """
    Read a previously saved generated test script.
    """
    safe_name = Path(filename).name
 
    if not safe_name:
        return "ERROR: No filename provided."
 
    path = OUTPUT_DIR / safe_name
    if not path.exists():
        return f"ERROR: File not found: {safe_name}"
 
    return path.read_text(encoding="utf-8")
 
 
def run_pytest(filename: str) -> str:
    """
    Run pytest on a generated test file and return a compact execution report.
    """
    safe_name = Path(filename).name
 
    if not safe_name:
        return "ERROR: No filename provided."
 
    test_path = OUTPUT_DIR / safe_name
    if not test_path.exists():
        return f"ERROR: File not found: {safe_name}"
 
    cmd = ["pytest", str(test_path), "-q"]
 
    try:
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return "ERROR: pytest timed out after 60 seconds."
    except FileNotFoundError:
        return (
            "ERROR: pytest is not installed or not available in the current environment. "
            "Install it with: pip install pytest"
        )
    except Exception as exc:
        return f"ERROR: Failed to run pytest: {exc}"
 
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
 
    return (
        f"COMMAND: {' '.join(cmd)}\n"
        f"RETURN_CODE: {result.returncode}\n\n"
        f"STDOUT:\n{stdout or '[no stdout]'}\n\n"
        f"STDERR:\n{stderr or '[no stderr]'}"
    )
 
 
def build_testing_agent():
    """
    Build a bounded Deep Agent for functional test generation.
    Uses the configured LLM provider from .env (via get_llm()).
    """
    model = get_llm(temperature=0)
 
    system_prompt = """
You are a functional test generation assistant.
 
Your job:
1. Understand the user's feature or API description.
2. Produce a concise functional test plan.
3. Generate a runnable pytest test script.
4. Save the script via save_test_script when the user asks to save it or when a filename is clearly provided.
5. If the user asks to validate or run the test, use run_pytest.
6. Summarize test execution results clearly.
7. If tests fail, explain why and propose a corrected version.
 
Rules:
- Do not delegate simple work to subagents.
- Prefer direct reasoning plus the provided tools.
- Generate Python pytest code only.
- For API tests, default to pytest plus requests unless stated otherwise.
- Keep assumptions explicit.
- When saving, choose a sensible filename if one is not provided.
- When the user asks to run tests, save the file first and then call run_pytest.
- Always structure the final answer in this format:
 
SECTION 1: FEATURE SUMMARY
SECTION 2: ASSUMPTIONS
SECTION 3: FUNCTIONAL TEST SCENARIOS
SECTION 4: GENERATED TEST SCRIPT
SECTION 5: EXECUTION RESULT
SECTION 6: SAVED FILE
 
For SECTION 4, include exactly one Python code block.
For SECTION 5, if tests were not run, say "Not run".
For SECTION 6, include the saved file path if saved, otherwise say "Not saved yet".
"""
 
    return create_deep_agent(
        model=model,
        tools=[save_test_script, read_test_script, run_pytest],
        system_prompt=system_prompt,
    )
