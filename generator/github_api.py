"""
GitHub API client for fetching profile data.
"""

import logging
import os
from typing import Dict, List

import requests


logger = logging.getLogger(__name__)


class GitHubAPI:
    """Simple GitHub REST API client."""

    REST_URL = "https://api.github.com"

    def __init__(self, username: str, token: str = None):
        self.username = username
        self.token = token or os.environ.get("GITHUB_TOKEN", "")

        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }

        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def _request(self, method: str, url: str, **kwargs):
        """Send a request to GitHub API."""
        kwargs.setdefault("headers", self.headers)

        response = requests.request(
            method,
            url,
            timeout=30,
            **kwargs
        )

        return response

    # ---------------------------------------------------------
    # Repositories
    # ---------------------------------------------------------

    def _paginate_repos(self):
        """Yield pages of public owned repositories."""
        page = 1

        while True:
            repos_resp = self._request(
                "GET",
                f"{self.REST_URL}/users/{self.username}/repos",
                params={
                    "per_page": 100,
                    "page": page,
                    "type": "owner",
                },
            )

            repos_resp.raise_for_status()

            repos = repos_resp.json()

            if not repos:
                break

            yield repos

            if len(repos) < 100:
                break

            page += 1

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def fetch_stats(self) -> dict:
        """Fetch GitHub profile statistics."""

        try:
            return self._fetch_stats_graphql()
        except Exception as e:
            logger.warning(
                "GraphQL stats failed, falling back to REST: %s",
                e,
            )
            return self._fetch_stats_rest()

    def _fetch_stats_graphql(self) -> dict:
        """Fetch statistics using GitHub GraphQL API."""

        if not self.token:
            return self._fetch_stats_rest()

        query = """
        query($login: String!) {
          user(login: $login) {
            repositories(
              first: 100
              ownerAffiliations: OWNER
              privacy: PUBLIC
            ) {
              totalCount
              nodes {
                stargazerCount
                forkCount
              }
            }

            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalIssueContributions
            }
          }
        }
        """

        response = self._request(
            "POST",
            "https://api.github.com/graphql",
            json={
                "query": query,
                "variables": {
                    "login": self.username
                },
            },
        )

        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            raise RuntimeError(data["errors"])

        user = data["data"]["user"]

        if user is None:
            raise RuntimeError("GitHub user not found")

        repositories = user["repositories"]

        total_stars = sum(
            repo["stargazerCount"]
            for repo in repositories["nodes"]
        )

        total_forks = sum(
            repo["forkCount"]
            for repo in repositories["nodes"]
        )

        contributions = user["contributionsCollection"]

        return {
            "commits": contributions["totalCommitContributions"],
            "prs": contributions["totalPullRequestContributions"],
            "issues": contributions["totalIssueContributions"],
            "repos": repositories["totalCount"],
            "stars": total_stars,
            "forks": total_forks,
        }

    def _fetch_stats_rest(self) -> dict:
        """Fetch statistics using GitHub REST API."""

        repositories = self.fetch_repositories()

        repositories = [
            repo
            for repo in repositories
            if not repo.get("fork")
        ]

        stars = sum(
            repo.get("stargazers_count", 0)
            for repo in repositories
        )

        forks = sum(
            repo.get("forks_count", 0)
            for repo in repositories
        )

        return {
            "commits": 0,
            "prs": 0,
            "issues": 0,
            "repos": len(repositories),
            "stars": stars,
            "forks": forks,
        }

    # ---------------------------------------------------------
    # Languages
    # ---------------------------------------------------------

    def fetch_languages(self) -> dict:
        """Fetch language byte counts across all owned non-fork repositories."""
        languages = {}
        page = 1

        while True:
            repos_resp = self._request(
                "GET",
                f"{self.REST_URL}/user/repos",
                params={
                    "per_page": 100,
                    "page": page,
                    "type": "all",
                    "affiliation": "owner",
                },
            )
            repos_resp.raise_for_status()
            repos = repos_resp.json()

            if not repos:
                break

            for repo in repos:
                if repo.get("fork"):
                    continue

                try:
                    lang_resp = self._request(
                        "GET",
                        repo["languages_url"],
                    )

                    if lang_resp.status_code == 200:
                        for lang, bytes_count in lang_resp.json().items():
                            languages[lang] = languages.get(lang, 0) + bytes_count
                    else:
                        logger.warning(
                            "Could not fetch languages for %s (HTTP %d)",
                            repo.get("full_name", "unknown"),
                            lang_resp.status_code,
                        )

                except requests.exceptions.RequestException as e:
                    logger.warning(
                        "Error fetching languages for %s: %s",
                        repo.get("full_name", "unknown"),
                        e,
                    )

            if len(repos) < 100:
                break

            page += 1

        return languages

    def fetch_user(self) -> dict:
        """Fetch GitHub user information."""

        response = self._request(
            "GET",
            f"{self.REST_URL}/users/{self.username}",
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------
    # Repository statistics
    # ---------------------------------------------------------

    def fetch_repositories(self) -> List[dict]:
        """Fetch all public repositories owned by the user."""

        repositories = []

        for repos in self._paginate_repos():
            repositories.extend(repos)

        return repositories

    # ---------------------------------------------------------
    # Contribution / profile statistics
    # ---------------------------------------------------------

    def count_repositories(self) -> int:
        """Count public repositories owned by the user."""

        repositories = self.fetch_repositories()

        return len(
            [
                repo
                for repo in repositories
                if not repo.get("fork")
            ]
        )

    def count_stars(self) -> int:
        """Count total stars across owned public repositories."""

        repositories = self.fetch_repositories()

        return sum(
            repo.get("stargazers_count", 0)
            for repo in repositories
            if not repo.get("fork")
        )

    def count_forks(self) -> int:
        """Count total forks across owned public repositories."""

        repositories = self.fetch_repositories()

        return sum(
            repo.get("forks_count", 0)
            for repo in repositories
            if not repo.get("fork")
        )
