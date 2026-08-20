#!/usr/bin/env python3
"""Render the Flask app into a static site for GitHub Pages.

GitHub Pages serves this repo as a project site at
https://lee-dohyun.github.io/architecture/, so every internal
absolute link (href="/..."/src="/...") rendered by Flask gets
prefixed with BASE_PATH before being written to disk.
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app, SUPPORTED_LANGS  # noqa: E402

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT_DIR, "dist")
BASE_PATH = os.environ.get("PAGES_BASE_PATH", "/architecture")

_LINK_RE = re.compile(r'(href|src)="/(?!/)')


def rewrite_links(html: str) -> str:
    if not BASE_PATH:
        return html
    return _LINK_RE.sub(f'\\1="{BASE_PATH}/', html)


def render(client, path: str) -> str:
    resp = client.get(path)
    if resp.status_code != 200:
        raise RuntimeError(f"GET {path} -> {resp.status_code}")
    return rewrite_links(resp.get_data(as_text=True))


def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    client = app.test_client()

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(render(client, "/"))

    for lang in SUPPORTED_LANGS:
        lang_dir = os.path.join(OUTPUT_DIR, lang)
        os.makedirs(lang_dir, exist_ok=True)
        with open(os.path.join(lang_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(render(client, f"/{lang}/"))

    shutil.copytree(
        os.path.join(ROOT_DIR, "static"),
        os.path.join(OUTPUT_DIR, "static"),
    )

    open(os.path.join(OUTPUT_DIR, ".nojekyll"), "w").close()

    print(f"Built static mirror -> {OUTPUT_DIR} (base path: {BASE_PATH!r})")


if __name__ == "__main__":
    main()
