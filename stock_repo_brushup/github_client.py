from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from stock_repo_brushup.models import RepositoryRecommendation
from stock_repo_brushup.report import render_markdown

GITHUB_API = "https://api.github.com"


class GitHubApiError(RuntimeError):
    pass


@dataclass(slots=True)
class GitHubClient:
    token: str | None = None
    api_url: str = GITHUB_API

    @classmethod
    def from_env(cls) -> "GitHubClient":
        return cls(token=os.getenv("TARGET_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN"))

    def _request(self, method: str, path: str, data: dict[str, Any] | None = None) -> Any:
        url = path if path.startswith("http") else f"{self.api_url}{path}"
        body = None if data is None else json.dumps(data).encode("utf-8")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "stock-repo-brushup-automation",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:  # noqa: S310
                raw = response.read().decode("utf-8")
                if not raw:
                    return None
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubApiError(f"GitHub API {method} {url} failed: {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise GitHubApiError(f"GitHub API {method} {url} failed: {exc}") from exc

    def list_repositories(self, owner: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        repos: list[dict[str, Any]] = []
        per_page = 100
        if owner:
            path_base = f"/users/{urllib.parse.quote(owner)}/repos?type=owner&sort=updated&per_page={per_page}"
        else:
            path_base = f"/user/repos?affiliation=owner&sort=updated&per_page={per_page}"
        page = 1
        while len(repos) < limit:
            batch = self._request("GET", f"{path_base}&page={page}")
            if not batch:
                break
            repos.extend(batch)
            if len(batch) < per_page:
                break
            page += 1
        return repos[:limit]

    def read_text_file(self, owner: str, repo: str, path: str, ref: str | None = None) -> str | None:
        suffix = f"?ref={urllib.parse.quote(ref)}" if ref else ""
        try:
            result = self._request("GET", f"/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}{suffix}")
        except GitHubApiError:
            return None
        if not isinstance(result, dict) or result.get("type") != "file":
            return None
        content = result.get("content")
        if not isinstance(content, str):
            return None
        try:
            return base64.b64decode(content).decode("utf-8", errors="replace")
        except ValueError:
            return None

    def read_common_files(self, owner: str, repo: str, default_branch: str) -> dict[str, str]:
        files: dict[str, str] = {}
        for path in [
            "README.md",
            "readme.md",
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "Pipfile",
            "environment.yml",
            "package.json",
            "docs/README.md",
        ]:
            content = self.read_text_file(owner, repo, path, ref=default_branch)
            if content is not None:
                files[path] = content
        return files

    def _get_ref_sha(self, owner: str, repo: str, branch: str) -> str:
        ref = self._request("GET", f"/repos/{owner}/{repo}/git/ref/heads/{urllib.parse.quote(branch)}")
        return str(ref["object"]["sha"])

    def create_branch(self, owner: str, repo: str, branch: str, base_branch: str) -> None:
        sha = self._get_ref_sha(owner, repo, base_branch)
        try:
            self._request(
                "POST",
                f"/repos/{owner}/{repo}/git/refs",
                {"ref": f"refs/heads/{branch}", "sha": sha},
            )
        except GitHubApiError as exc:
            if "Reference already exists" not in str(exc):
                raise

    def _existing_file_sha(self, owner: str, repo: str, path: str, branch: str) -> str | None:
        try:
            result = self._request(
                "GET",
                f"/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}?ref={urllib.parse.quote(branch)}",
            )
        except GitHubApiError:
            return None
        if isinstance(result, dict) and result.get("sha"):
            return str(result["sha"])
        return None

    def put_file(self, owner: str, repo: str, path: str, content: str, branch: str, message: str) -> None:
        payload: dict[str, Any] = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        sha = self._existing_file_sha(owner, repo, path, branch)
        if sha:
            payload["sha"] = sha
        self._request("PUT", f"/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}", payload)

    def create_pull_request(
        self, owner: str, repo: str, branch: str, base_branch: str, title: str, body: str
    ) -> str:
        try:
            result = self._request(
                "POST",
                f"/repos/{owner}/{repo}/pulls",
                {"title": title, "head": branch, "base": base_branch, "body": body},
            )
        except GitHubApiError as exc:
            if "A pull request already exists" in str(exc):
                pulls = self._request(
                    "GET",
                    f"/repos/{owner}/{repo}/pulls?head={owner}:{urllib.parse.quote(branch)}&state=open",
                )
                if pulls:
                    return str(pulls[0].get("html_url", ""))
            raise
        return str(result.get("html_url", ""))


def build_pr_files(item: RepositoryRecommendation) -> dict[str, str]:
    markdown = render_markdown([item], apply_mode=True)
    packages = sorted({rec.package for rec in item.recommendations})
    requirements = "\n".join(packages) + ("\n" if packages else "")
    return {
        "docs/stock-investment-brushup.md": markdown,
        "requirements.stock-investment-brushup.txt": requirements,
    }


def apply_brushup_pr(client: GitHubClient, item: RepositoryRecommendation) -> str:
    owner, repo = item.repository.owner_repo
    if not owner or not repo:
        raise GitHubApiError(f"Invalid repository full_name: {item.repository.full_name}")
    branch = "stock-investment-brushup-" + time.strftime("%Y%m%d%H%M%S")
    client.create_branch(owner, repo, branch, item.repository.default_branch)
    for path, content in build_pr_files(item).items():
        client.put_file(
            owner,
            repo,
            path,
            content,
            branch,
            "Add stock investment brush-up recommendations",
        )
    body = (
        "このPRは stock-repo-brushup-automation により作成されました。\n\n"
        "既存コードを直接変更せず、まず `docs/stock-investment-brushup.md` と "
        "`requirements.stock-investment-brushup.txt` に改善候補を追加しています。\n"
        "内容を確認した上で、必要なライブラリだけ段階的に導入してください。"
    )
    return client.create_pull_request(
        owner,
        repo,
        branch,
        item.repository.default_branch,
        "Add stock investment OSS brush-up recommendations",
        body,
    )
