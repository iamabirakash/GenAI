"""Update the auto-generated project overview in README.md.

This script intentionally edits only the section between the marker comments.
Everything outside those markers remains hand-written documentation.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
REQUIREMENTS = ROOT / "requirements.txt"
START = "<!-- AUTO-GENERATED-README-START -->"
END = "<!-- AUTO-GENERATED-README-END -->"

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", "node_modules"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.relative_to(ROOT).as_posix() == "scripts/update_readme.py":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def string_literals(tree: ast.AST) -> list[str]:
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)
    return values


def import_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def call_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
    return names


def env_vars(tree: ast.AST) -> set[str]:
    vars_found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "getenv":
            continue
        if not node.args:
            continue
        arg = node.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            vars_found.add(arg.value)
    return vars_found


def model_names(tree: ast.AST) -> set[str]:
    models: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Name):
            continue
        if func.id not in {"ChatOpenAI", "ChatAnthropic", "ChatGoogleGenerativeAI", "ChatGroq"}:
            continue
        for keyword in node.keywords:
            if keyword.arg == "model" and isinstance(keyword.value, ast.Constant):
                if isinstance(keyword.value.value, str):
                    models.add(keyword.value.value)
    return models


def summarize_file(path: Path) -> dict[str, object]:
    rel = path.relative_to(ROOT).as_posix()
    text = read_text(path)
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {
            "path": rel,
            "kind": "Python file",
            "features": ["contains syntax errors"],
            "env": [],
            "models": [],
        }

    imports = import_names(tree)
    calls = call_names(tree)
    literals = "\n".join(string_literals(tree)).lower()

    features: list[str] = []
    kind = "Python module"

    if "streamlit" in imports:
        kind = "Streamlit app"
        features.append("web UI")
    elif "input" in calls:
        kind = "CLI app"
        features.append("terminal input")

    if any(name.startswith("langchain") for name in imports):
        features.append("LangChain")
    if "RunnableParallel" in text:
        features.append("parallel chain")
    if "RunnablePassthrough" in text:
        features.append("derived output step")
    if "PromptTemplate" in text or "ChatPromptTemplate" in text:
        features.append("prompt templates")

    if "travel" in literals or "itinerary" in literals:
        features.append("travel planning")
    if "joke" in literals or "comedy" in literals:
        features.append("joke generation")
    if "college" in literals or "university" in literals:
        features.append("college guidance")

    return {
        "path": rel,
        "kind": kind,
        "features": sorted(set(features)),
        "env": sorted(env_vars(tree)),
        "models": sorted(model_names(tree)),
    }


def requirements() -> list[str]:
    if not REQUIREMENTS.exists():
        return []
    packages = []
    for raw_line in read_text(REQUIREMENTS).splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            packages.append(line)
    return packages


def generated_section() -> str:
    summaries = [summarize_file(path) for path in iter_python_files()]
    packages = requirements()

    lines = [
        START,
        "## Auto-Generated Project Overview",
        "",
        "This section is generated by `scripts/update_readme.py`. Manual edits should go outside the marker comments.",
        "",
        "### Python Entry Points",
    ]

    for item in summaries:
        features = item["features"]
        feature_text = "; ".join(features) if features else "general Python code"
        lines.append(f"- `{item['path']}`: {item['kind']} with {feature_text}.")

    if packages:
        lines.extend(["", "### Dependencies"])
        lines.extend(f"- `{package}`" for package in packages)

    env_values = sorted({env for item in summaries for env in item["env"]})
    if env_values:
        lines.extend(["", "### Environment Variables"])
        lines.extend(f"- `{env}`" for env in env_values)

    model_values = sorted({model for item in summaries for model in item["models"]})
    if model_values:
        lines.extend(["", "### Referenced Models"])
        lines.extend(f"- `{model}`" for model in model_values)

    lines.extend([END, ""])
    return "\n".join(lines)


def update_readme() -> None:
    section = generated_section()
    if README.exists():
        current = read_text(README)
    else:
        current = "# GenAI\n\n"

    if START in current and END in current:
        before = current.split(START, 1)[0].rstrip()
        after = current.split(END, 1)[1].lstrip()
        updated = f"{before}\n\n{section}\n{after}".rstrip() + "\n"
    else:
        updated = current.rstrip() + "\n\n" + section

    README.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    update_readme()
