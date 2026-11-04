#!/usr/bin/env python3
"""Generate GitHub and GitHub Pages navigation from Qoder wiki metadata."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT / "content"
METADATA_PATH = ROOT / "meta" / "repowiki-metadata.json"
SOURCE_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(file://([^\s)]+)\)")


def filesystem_name(name: str) -> str:
    """Match the exporter's filename sanitization for slash-containing titles."""
    return re.sub(r"[/\\]+", "_", name)


def load_catalogs() -> dict[str, dict]:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    catalogs = metadata["wiki_catalogs"]
    return {catalog["id"]: catalog for catalog in catalogs}


def build_catalog_tree(catalogs: dict[str, dict]) -> dict[str | None, list[dict]]:
    children: dict[str | None, list[dict]] = {}
    for catalog in catalogs.values():
        parent_id = catalog.get("parent_id") or None
        children.setdefault(parent_id, []).append(catalog)

    def sort_key(catalog: dict) -> tuple[int, int, str]:
        # Getting Started is the intentional first chapter; the remaining root
        # chapters use the order emitted by the wiki generator.
        is_getting_started = catalog["name"] == "Getting Started"
        order = catalog.get("order")
        return (0 if is_getting_started else 1, order if order is not None else 0, catalog["name"])

    for siblings in children.values():
        siblings.sort(key=sort_key)
    return children


def catalog_directory(
    catalog: dict,
    catalogs: dict[str, dict],
    children: dict[str | None, list[dict]],
) -> Path:
    parent_id = catalog.get("parent_id") or None
    if parent_id is None:
        return CONTENT_ROOT / filesystem_name(catalog["name"])
    parent = catalogs[parent_id]
    return catalog_directory(parent, catalogs, children) / filesystem_name(catalog["name"])


def catalog_file_path(
    catalog: dict,
    catalogs: dict[str, dict],
    children: dict[str | None, list[dict]],
) -> Path:
    parent_id = catalog.get("parent_id") or None
    if parent_id is None:
        if children.get(catalog["id"]):
            return catalog_directory(catalog, catalogs, children) / f"{filesystem_name(catalog['name'])}.md"
        return CONTENT_ROOT / f"{filesystem_name(catalog['name'])}.md"

    parent = catalogs[parent_id]
    if children.get(catalog["id"]):
        return catalog_directory(catalog, catalogs, children) / f"{filesystem_name(catalog['name'])}.md"
    return catalog_directory(parent, catalogs, children) / f"{filesystem_name(catalog['name'])}.md"


def site_link(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    return quote(relative, safe="/._-~")


def render_sidebar(catalogs: dict[str, dict], children: dict[str | None, list[dict]]) -> str:
    lines = ["- [Wiki Overview](README.md)"]

    def visit(catalog: dict, depth: int) -> None:
        indent = "  " * depth
        path = catalog_file_path(catalog, catalogs, children)
        lines.append(f"{indent}- [{catalog['name']}]({site_link(path)})")
        for child in children.get(catalog["id"], []):
            visit(child, depth + 1)

    for root in children.get(None, []):
        visit(root, 0)
    return "\n".join(lines) + "\n"


def render_readme(catalogs: dict[str, dict], children: dict[str | None, list[dict]]) -> str:
    lines = [
        "# Optimist.Orchestrator Wiki",
        "",
        "> Public technical documentation for the Optimist.Orchestrator ETSI MEC edge-orchestration platform.",
        "> The documentation was generated from the repository wiki export and organized into browsable chapters.",
        "",
        "## Browse the wiki",
        "",
        "Once GitHub Pages is enabled, its deployed site provides the full sidebar, search, and Mermaid diagram rendering; the repository tree below remains directly browsable on GitHub.",
        "See the [publishing and update guide](PUBLISHING.md) to enable GitHub Pages and refresh the wiki.",
        "You can also browse every Markdown page directly from the repository tree below.",
        "",
    ]

    def visit(catalog: dict, depth: int) -> None:
        path = catalog_file_path(catalog, catalogs, children)
        indent = "  " * depth
        lines.append(f"{indent}- [{catalog['name']}]({site_link(path)})")
        for child in children.get(catalog["id"], []):
            visit(child, depth + 1)

    for root in children.get(None, []):
        visit(root, 0)

    lines.extend(
        [
            "",
            "## Documentation scope",
            "",
            "The chapters cover the system architecture, bounded contexts, core services, ETSI APIs, Temporal workflows, placement, data models, security, deployment, testing, observability, development guidance, architecture decisions, and troubleshooting.",
            "",
            "> Source-code references in the generated pages are shown as paths because this repository contains the documentation showcase rather than the original source tree.",
            "",
            "## Local preview",
            "",
            "Run `uv run --no-project python -m http.server 8000` from the repository root, then open `http://localhost:8000`.",
            "",
        ]
    )
    return "\n".join(lines)


def repair_source_links() -> int:
    replacements = 0
    for markdown_path in CONTENT_ROOT.rglob("*.md"):
        original = markdown_path.read_text(encoding="utf-8")

        def replace(match: re.Match[str]) -> str:
            nonlocal replacements
            replacements += 1
            return f"`{match.group(2)}`"

        repaired = SOURCE_LINK_PATTERN.sub(replace, original)
        if repaired != original:
            markdown_path.write_text(repaired, encoding="utf-8")
    return replacements


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repair-source-links",
        action="store_true",
        help="Convert unavailable file:// source links into visible source paths.",
    )
    args = parser.parse_args()

    catalogs = load_catalogs()
    children = build_catalog_tree(catalogs)

    missing = [
        str(catalog_file_path(catalog, catalogs, children).relative_to(ROOT))
        for catalog in catalogs.values()
        if not catalog_file_path(catalog, catalogs, children).exists()
    ]
    if missing:
        raise SystemExit("Metadata pages missing from content/:\n" + "\n".join(missing))

    (ROOT / "_sidebar.md").write_text(render_sidebar(catalogs, children), encoding="utf-8")
    (ROOT / "README.md").write_text(render_readme(catalogs, children), encoding="utf-8")

    if args.repair_source_links:
        print(f"Repaired {repair_source_links()} unavailable source links.")
    print(f"Generated navigation for {len(catalogs)} wiki pages.")


if __name__ == "__main__":
    main()
