#!/usr/bin/env python3
import argparse
import logging
import os
import sys

import requests


DEFAULT_OWNER = os.getenv("GITHUB_OWNER", "your-owner")
DEFAULT_REPO = os.getenv("GITHUB_REPO", "your-repo")
DEFAULT_WORKFLOW = os.getenv("GITHUB_WORKFLOW_FILE", "your-workflow.yml")
DEFAULT_BRANCH = os.getenv("GITHUB_BRANCH", "main")
DEFAULT_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("dispatch_private_workflow")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dispatch a GitHub Actions workflow securely from the local environment or CI."
    )
    parser.add_argument("--owner", default=DEFAULT_OWNER, help="GitHub repository owner.")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub repository name.")
    parser.add_argument("--workflow", default=DEFAULT_WORKFLOW, help="Workflow file path or name.")
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help="Branch or ref to dispatch.")
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help="GitHub API base URL (useful for enterprise instances).",
    )
    return parser.parse_args()


def _safe_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
        message = payload.get("message") or payload.get("error")
    except ValueError:
        message = response.text.strip()[:200] or "sin detalle disponible"

    return f"HTTP {response.status_code}: {message}"


def main() -> int:
    args = parse_args()

    token = os.getenv("PRIVATE_REPO_TOKEN", "").strip()
    owner = args.owner.strip()
    repo = args.repo.strip()
    workflow = args.workflow.strip()
    branch = args.branch.strip()
    api_url = args.api_url.rstrip("/")

    if not token:
        logger.error("Falta PRIVATE_REPO_TOKEN en el entorno.")
        return 1

    if not all([owner, repo, workflow, branch, api_url]):
        logger.error("owner, repo, workflow, branch y api-url deben estar configurados.")
        return 1

    url = f"{api_url}/repos/{owner}/{repo}/actions/workflows/{workflow}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"ref": branch}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as exc:
        logger.exception("Error de conexión al enviar el dispatch.")
        logger.error("Detalle: %s", exc)
        return 1

    if response.status_code >= 400:
        logger.error("Dispatch fallido: %s", _safe_error_message(response))
        logger.error("Destino: %s/%s | workflow=%s | ref=%s", owner, repo, workflow, branch)
        return 1

    logger.info("Dispatch enviado correctamente a %s/%s (%s @ %s).", owner, repo, workflow, branch)
    logger.info("Status HTTP: %s", response.status_code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
