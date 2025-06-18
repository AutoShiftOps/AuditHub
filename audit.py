import requests
import argparse
import json
from datetime import datetime, timedelta

GITHUB_API = "https://api.github.com"


def get_headers(token):
    return {"Authorization": f"token {token}"}


def is_old(date_str):
    created = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return (datetime.utcnow() - created) > timedelta(days=30)


def check_repo_health(token, repo):
    headers = get_headers(token)
    report = {"repo": repo}

    # Get branches
    branches_url = f"{GITHUB_API}/repos/{repo}/branches"
    branches = requests.get(branches_url, headers=headers).json()
    report["branch_count"] = len(branches)

    # Check open PRs > 30 days old
    prs_url = f"{GITHUB_API}/repos/{repo}/pulls?state=open"
    prs = requests.get(prs_url, headers=headers).json()
    old_prs = [pr["html_url"] for pr in prs if "created_at" in pr and is_old(pr["created_at"])]
    report["open_prs_over_30_days"] = old_prs

    # Check for README
    contents_url = f"{GITHUB_API}/repos/{repo}/contents"
    contents = requests.get(contents_url, headers=headers).json()
    filenames = [f["name"].lower() for f in contents if "name" in f]
    report["missing_readme"] = "readme.md" not in filenames

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="GitHub token")
    parser.add_argument("--repo", required=True, help="Repo in owner/name format")
    args = parser.parse_args()

    output = check_repo_health(args.token, args.repo)
    print(json.dumps(output, indent=2))
