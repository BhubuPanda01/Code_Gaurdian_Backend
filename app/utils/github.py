"""
GitHub URL Validation and Utilities
"""
import re
from urllib.parse import urlparse


def validate_github_url(github_url: str) -> tuple[bool, str, str]:
    """
    Validate GitHub URL and extract repository info
    
    Args:
        github_url: GitHub repository URL
        
    Returns:
        tuple: (is_valid, repository_name, error_message)
    """
    try:
        # Remove trailing slashes and whitespace
        github_url = github_url.strip().rstrip('/')
        
        # Check if URL starts with http/https
        if not github_url.startswith(('http://', 'https://')):
            return False, "", "URL must start with http:// or https://"
        
        # Check if it's a github.com URL
        parsed_url = urlparse(github_url)
        if not parsed_url.netloc or 'github.com' not in parsed_url.netloc:
            return False, "", "URL must be a GitHub repository URL"
        
        # Extract owner and repository from path
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            return False, "", "Invalid GitHub URL format. Expected: https://github.com/owner/repo"
        
        owner = path_parts[0]
        repo = path_parts[1].rstrip('.git')
        
        # Validate owner and repo names (GitHub naming rules)
        github_name_pattern = r'^[a-zA-Z0-9_-]+$'
        
        if not re.match(github_name_pattern, owner):
            return False, "", f"Invalid GitHub owner name: {owner}"
        
        if not re.match(github_name_pattern, repo):
            return False, "", f"Invalid GitHub repository name: {repo}"
        
        repository_name = f"{owner}/{repo}"
        
        return True, repository_name, ""
    
    except Exception as e:
        return False, "", f"Error validating GitHub URL: {str(e)}"


def normalize_github_url(github_url: str) -> str:
    """
    Normalize GitHub URL to standard format
    
    Args:
        github_url: GitHub repository URL
        
    Returns:
        str: Normalized URL
    """
    github_url = github_url.strip().rstrip('/')
    if github_url.endswith('.git'):
        github_url = github_url[:-4]
    return github_url
