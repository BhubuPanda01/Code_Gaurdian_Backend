"""
Repository analysis helpers.
"""
import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any, List


def clone_repository(github_url: str) -> str:
    """Clone repository into a temporary folder and return path."""
    target_dir = tempfile.mkdtemp(prefix="code_guardian_repo_")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", github_url, target_dir],
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")
        return target_dir
    except Exception:
        shutil.rmtree(target_dir, ignore_errors=True)
        raise


def analyze_repository(path: str) -> Dict[str, Any]:
    """Scan repository content and return analysis summary."""
    summary = {
        "languages": {},
        "total_files": 0,
        "total_lines": 0,
        "issues": [],
        "suggestions": [],
    }

    for root, _, files in os.walk(path):
        for file in files:
            summary["total_files"] += 1
            filepath = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            lang = ext.lower().lstrip('.') or "unknown"

            summary["languages"].setdefault(lang, 0)
            summary["languages"][lang] += 1

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                summary["total_lines"] += len(lines)
                if len(lines) > 1000:
                    summary["issues"].append(
                        f"Large file: {os.path.relpath(filepath, path)} has {len(lines)} lines"
                    )
            except OSError:
                continue

    # Basic heuristic checks
    if summary["total_files"] == 0:
        summary["issues"].append("Repository has no files.")

    if summary["languages"].get("py", 0) > 0:
        summary["suggestions"].append("Run formatted linting on Python files (black + pylint/ruff).")

    if summary["total_lines"] > 20000:
        summary["suggestions"].append("Large codebase, split analysis into modules and use CI caching.")

    if summary["languages"].get("js", 0) + summary["languages"].get("ts", 0) > 0:
        summary["suggestions"].append("Check for unneeded dependencies in package.json and apply bundle optimization.")

    return summary


def generate_optimization_recommendations(analysis_summary: Dict[str, Any]) -> List[str]:
    """Generate AI-like optimization suggestions from analysis summary."""
    recommendations = []

    recommendations.append("Repository scan completed.")

    if analysis_summary.get("issues"):
        recommendations.append("Found potential high-risk areas:")
        recommendations.extend(analysis_summary.get("issues", [])[:5])

    recommendations.extend(analysis_summary.get("suggestions", []))

    if not analysis_summary.get("suggestions"):
        recommendations.append("No obvious optimizations detected; run static analyzers for deeper insight.")

    return recommendations
