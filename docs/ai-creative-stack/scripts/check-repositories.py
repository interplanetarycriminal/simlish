#!/usr/bin/env python3
"""Check upstream GitHub metadata for canonical URL and archive changes."""
import json
import os
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    entries = json.loads((ROOT / "registry/repositories.json").read_text(encoding="utf-8"))
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):  # optional: lifts the 60 requests per hour anonymous limit
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    errors = 0
    for entry in entries:
        # A redirected entry's original URL is known to be gone; check its recorded canonical URL instead.
        redirected = entry["verification_status"] == "redirected"
        origin = urlsplit(entry["verified_url"] if redirected else entry["original_url"])
        if redirected:
            print(f"{entry['id']}: original {entry['original_url']} recorded as redirected; checking {entry['verified_url']}")
        if origin.scheme != "https" or origin.netloc != "github.com":
            print(f"{entry['id']}: invalid GitHub URL", file=sys.stderr)
            errors += 1
            continue
        owner, repo, *suffix = origin.path.strip("/").split("/")
        url = f"https://api.github.com/repos/{owner}/{repo}"
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=10) as response:
                data = json.load(response)
            canonical = "/".join([data["html_url"], *suffix])
            changed = (canonical != entry["verified_url"] or data["archived"] != entry["maintenance"]["archived"]
                       or data["default_branch"] != entry["maintenance"]["default_branch"])
            errors += int(changed)
            print(f"{entry['id']} {canonical} branch={data['default_branch']} archived={data['archived']} pushed={data['pushed_at']} changed={changed}")
        except (URLError, TimeoutError) as error:
            errors += 1
            print(f"{entry['id']}: GitHub request failed ({error})", file=sys.stderr)
    return int(errors > 0)


if __name__ == "__main__":
    sys.exit(main())
