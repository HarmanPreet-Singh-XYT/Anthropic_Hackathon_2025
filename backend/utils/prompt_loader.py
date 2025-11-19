"""
Prompt loading utility with template variable substitution
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Set


def load_prompt(prompt_name: str, variables: Dict[str, Any] = None) -> str:
    """
    Load a prompt template from the prompts directory and substitute variables

    Args:
        prompt_name: Name of the prompt file (without .md extension)
        variables: Dict of variable names to values for substitution

    Returns:
        Prompt text with variables substituted

    Raises:
        FileNotFoundError: If prompt file doesn't exist
        KeyError: If required variable is missing

    Example:
        >>> load_prompt("decoder", {"scholarship_text": "..."})
        "You are an expert Scholarship Strategist..."
    """
    variables = variables or {}

    # Construct path to prompt file
    prompts_dir = Path(__file__).parent.parent / "prompts"
    prompt_path = prompts_dir / f"{prompt_name}.md"

    # Check if file exists
    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file '{prompt_name}.md' not found in {prompts_dir}. "
            f"Available prompts: {', '.join(list_available_prompts())}"
        )

    # Read markdown file
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Extract all variables from template
    required_vars = _extract_variables(prompt_template)

    # Check for missing variables
    missing_vars = required_vars - set(variables.keys())
    if missing_vars:
        raise KeyError(
            f"Missing required variables for prompt '{prompt_name}': {', '.join(sorted(missing_vars))}"
        )

    # Substitute variables
    prompt_text = prompt_template
    for var_name, var_value in variables.items():
        placeholder = f"{{{var_name}}}"
        prompt_text = prompt_text.replace(placeholder, str(var_value))

    return prompt_text


def list_available_prompts() -> List[str]:
    """
    List all available prompt templates

    Returns:
        List of prompt names (without .md extension)
    """
    prompts_dir = Path(__file__).parent.parent / "prompts"

    if not prompts_dir.exists():
        return []

    # Find all .md files and return their names without extension
    prompt_files = prompts_dir.glob("*.md")
    return sorted([f.stem for f in prompt_files])


def validate_prompt_variables(prompt_name: str, variables: Dict[str, Any]) -> bool:
    """
    Check if all required variables for a prompt are provided

    Args:
        prompt_name: Name of the prompt file
        variables: Dict of provided variables

    Returns:
        True if all required variables present, False otherwise
    """
    try:
        prompts_dir = Path(__file__).parent.parent / "prompts"
        prompt_path = prompts_dir / f"{prompt_name}.md"

        if not prompt_path.exists():
            return False

        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        required_vars = _extract_variables(prompt_template)
        provided_vars = set(variables.keys())

        return required_vars.issubset(provided_vars)

    except Exception:
        return False


def _extract_variables(template: str) -> Set[str]:
    """
    Extract all {variable} placeholders from a template

    Args:
        template: Prompt template text

    Returns:
        Set of variable names found in template
    """
    # Find all {variable} patterns
    pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
    matches = re.findall(pattern, template)
    return set(matches)


def get_prompt_info(prompt_name: str) -> Dict[str, Any]:
    """
    Get metadata about a prompt template

    Args:
        prompt_name: Name of the prompt file

    Returns:
        Dict containing:
            - name: Prompt name
            - path: Full path to file
            - required_variables: List of required variables
            - size: File size in bytes
            - exists: Whether file exists

    Example:
        >>> info = get_prompt_info("decoder")
        >>> print(info["required_variables"])
        ["scholarship_text"]
    """
    prompts_dir = Path(__file__).parent.parent / "prompts"
    prompt_path = prompts_dir / f"{prompt_name}.md"

    info = {
        "name": prompt_name,
        "path": str(prompt_path),
        "exists": prompt_path.exists(),
        "required_variables": [],
        "size": 0
    }

    if prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()

        info["required_variables"] = sorted(list(_extract_variables(template)))
        info["size"] = prompt_path.stat().st_size

    return info
