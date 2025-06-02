# AuditHub

AuditHub is a lightweight Python CLI tool that checks the health of your GitHub repositories.

## Features

- Detects missing README or license
- Flags stale pull requests (older than 30 days)
- Outputs a clean JSON audit report

## Usage

```bash
python audit.py --token YOUR_GITHUB_TOKEN --owner your_org --repo your_repo
```

## License

MIT