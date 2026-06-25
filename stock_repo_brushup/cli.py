from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from stock_repo_brushup.github_client import GitHubApiError, GitHubClient, apply_brushup_pr
from stock_repo_brushup.models import RepositoryProfile
from stock_repo_brushup.recommendations import build_repository_recommendation
from stock_repo_brushup.report import write_outputs
from stock_repo_brushup.sample_data import sample_repositories


def _profile_from_github(raw: dict[str, Any], files: dict[str, str]) -> RepositoryProfile:
    profile = RepositoryProfile.from_mapping(raw)
    profile.files = files
    return profile


def run_github_scan(args: argparse.Namespace) -> int:
    client = GitHubClient.from_env()
    try:
        raw_repos = client.list_repositories(owner=args.owner, limit=args.limit)
    except GitHubApiError as exc:
        print(f"GitHub scan failed: {exc}", file=sys.stderr)
        return 2

    results = []
    pull_requests: list[dict[str, str]] = []
    for raw in raw_repos:
        profile = RepositoryProfile.from_mapping(raw)
        owner, repo_name = profile.owner_repo
        files = client.read_common_files(owner, repo_name, profile.default_branch) if owner and repo_name else {}
        item = build_repository_recommendation(_profile_from_github(raw, files))
        if item.repository.relevance_score >= args.min_score:
            results.append(item)
            if args.apply and item.should_apply:
                try:
                    pr_url = apply_brushup_pr(client, item)
                    pull_requests.append({"repository": item.repository.full_name, "pull_request": pr_url})
                except GitHubApiError as exc:
                    pull_requests.append({"repository": item.repository.full_name, "error": str(exc)})

    output_dir = Path(args.output)
    write_outputs(results, output_dir, apply_mode=args.apply)
    if pull_requests:
        (output_dir / "pull-requests.json").write_text(
            json.dumps(pull_requests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"Wrote report to {output_dir / 'stock-investment-repo-report.md'}")
    print(f"Detected {len(results)} investment-related repositories")
    if pull_requests:
        print(f"PR results: {output_dir / 'pull-requests.json'}")
    return 0


def run_sample(args: argparse.Namespace) -> int:
    items = [build_repository_recommendation(repo) for repo in sample_repositories()]
    items = [item for item in items if item.repository.relevance_score >= args.min_score]
    write_outputs(items, Path(args.output), apply_mode=False)
    print(f"Wrote sample report to {Path(args.output) / 'stock-investment-repo-report.md'}")
    return 0


def run_local_scan(args: argparse.Namespace) -> int:
    root = Path(args.path)
    profiles: list[RepositoryProfile] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        files: dict[str, str] = {}
        for rel in ["README.md", "readme.md", "requirements.txt", "pyproject.toml", "package.json"]:
            candidate = child / rel
            if candidate.exists() and candidate.is_file():
                files[rel] = candidate.read_text(encoding="utf-8", errors="replace")
        profiles.append(
            RepositoryProfile(
                name=child.name,
                full_name=child.name,
                html_url=str(child.resolve()),
                language="Python" if any(path.endswith((".py", ".ipynb")) for path in files) else "",
                files=files,
            )
        )
    items = [build_repository_recommendation(repo) for repo in profiles]
    items = [item for item in items if item.repository.relevance_score >= args.min_score]
    write_outputs(items, Path(args.output), apply_mode=False)
    print(f"Wrote local report to {Path(args.output) / 'stock-investment-repo-report.md'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan GitHub repositories and recommend stock investment OSS improvements.")
    sub = parser.add_subparsers(dest="command", required=True)

    github_scan = sub.add_parser("github-scan", help="Scan GitHub repositories by owner and optionally open safe PRs.")
    github_scan.add_argument("--owner", help="GitHub user or organization. If omitted, authenticated user repos are scanned.")
    github_scan.add_argument("--limit", type=int, default=100)
    github_scan.add_argument("--min-score", type=int, default=4)
    github_scan.add_argument("--output", default="reports")
    github_scan.add_argument("--apply", action="store_true", help="Create safe recommendation PRs in target repos.")
    github_scan.set_defaults(func=run_github_scan)

    local_scan = sub.add_parser("scan-local", help="Scan local repository folders.")
    local_scan.add_argument("--path", default=".")
    local_scan.add_argument("--min-score", type=int, default=4)
    local_scan.add_argument("--output", default="reports")
    local_scan.set_defaults(func=run_local_scan)

    sample = sub.add_parser("sample", help="Generate a report from built-in sample repositories.")
    sample.add_argument("--min-score", type=int, default=4)
    sample.add_argument("--output", default="reports")
    sample.set_defaults(func=run_sample)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
