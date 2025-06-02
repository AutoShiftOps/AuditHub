import requests
import argparse
import json

GITHUB_API = "https://api.github.com"

def get_headers(token):
    return {"Authorization": f"token {token}"}

def check_repo_health(token, repo):
    headers = get_headers(token)
    report = {"repo": repo}

    # Get branches
    branches = requests.get(f"{GITHUB_API}/repos/{repo}/branches", headers=headers).json()
    report["branch_count"] = len(branches)

    # Check open PRs > 30 days old
    prs = requests.get(f"{GITHUB_API}/repos/{repo}/pulls?state=open", headers=headers).json()
    old_prs = [pr["html_url"] for pr in prs if "created_at" in pr and is_old(pr["created_at"])]
    report["open_prs_over_30_days"] = old_prs

    # Check for README
    contents = requests.get(f"{GITHUB_API}/repos/{repo}/contents", headers=headers).json()
    filenames = [f["name"].lower() for f in contents if "name" in f]
    report["missing_readme"] = "readme.md" not in filenames

    return report

def is_old(date_str):
    from datetime import datetime, timedelta
    created = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return (datetime.utcnow() - created) > timedelta(days=30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="GitHub token")
    parser.add_argument("--repo", required=True, help="Repo in owner/name format")
    args = parser.parse_args()

    output = check_repo_health(args.token, args.repo)
    print(json.dumps(output, indent=2))
