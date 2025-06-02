import argparse
import requests
import json
from datetime import datetime, timedelta

def get_headers(token):
    return {'Authorization': f'token {token}'}

def get_repo_metadata(owner, repo, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(url, headers=headers)
    data = r.json()
    return {
        "has_readme": data.get("has_wiki", False),
        "license": data.get("license", {}).get("name", "None")
    }

def get_stale_prs(owner, repo, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=open"
    r = requests.get(url, headers=headers)
    prs = r.json()
    stale_prs = []
    cutoff = datetime.now(datetime.timezone.utc) - timedelta(days=30)
    for pr in prs:
        updated_at = datetime.strptime(pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
        if updated_at < cutoff:
            stale_prs.append(pr["html_url"])
    return stale_prs

def audit_repo(token, owner, repo):
    headers = get_headers(token)
    metadata = get_repo_metadata(owner, repo, headers)
    stale_prs = get_stale_prs(owner, repo, headers)
    report = {
        "repo": f"{owner}/{repo}",
        "metadata": metadata,
        "stale_pull_requests": stale_prs
    }
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AuditHub CLI")
    parser.add_argument("--token", required=True, help="GitHub token")
    parser.add_argument("--owner", required=True, help="GitHub owner/org")
    parser.add_argument("--repo", required=True, help="GitHub repository")
    args = parser.parse_args()
    audit_repo(args.token, args.owner, args.repo)