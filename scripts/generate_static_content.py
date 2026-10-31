#!/usr/bin/env python3
"""Render blog and project cards into the static HTML pages."""

import html
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "blog" / "blog-map.json"
SITE_URL = "https://db-vol-1.github.io/portfolio/"
HTML_FILES = [
    ROOT / "index.html",
    ROOT / "blog" / "browse.html",
    ROOT / "pages" / "projects.html",
]


def absolute_url(path: str) -> str:
    return urljoin(SITE_URL, path.lstrip("./"))


def format_date(value: str) -> str:
    date = datetime.strptime(value, "%Y-%m-%d")
    return f"{date.strftime('%B')} {date.day}, {date.year}"


def render_blog_posts(posts: list[dict]) -> str:
    cards = []
    for post in sorted(posts, key=lambda item: item["date"], reverse=True):
        relative_url = post["url"].lstrip("./")
        if not (ROOT / relative_url).is_file():
            continue
        cards.append(
            f"""        <article class="blog-post-card">
            <img src="{html.escape(absolute_url(post["image"]))}" alt="{html.escape(post["title"])} post">
            <div>
                <h3><a href="{html.escape(absolute_url(relative_url))}">{html.escape(post["title"])}</a></h3>
                <p>{html.escape(post["description"])}</p>
                <time datetime="{html.escape(post["date"])}">{format_date(post["date"])}</time>
            </div>
        </article>"""
        )
    return "\n".join(cards)


def render_projects(projects: list[dict]) -> str:
    sorted_projects = sorted(
        projects,
        key=lambda project: (
            project["ended"] is not None,
            project["started"],
            project["ended"] or "",
        ),
    )
    cards = []
    for project in sorted_projects:
        details = [
            f'                <h3>{html.escape(project["title"])}</h3>',
            f'                <p>{html.escape(project["description"])}</p>',
            f'                <time datetime="{html.escape(project["started"])}">'
            f'{format_date(project["started"])} - '
            f'{("Current" if project["ended"] is None else format_date(project["ended"]))}'
            "</time>",
        ]
        if project.get("related_blog_posts"):
            details.append(
                f'                <a class="read-more" href="{html.escape(absolute_url(project["related_blog_posts"][0]))}">Read more</a>'
            )
        if project.get("github_url"):
            details.append(
                f'                <a class="read-more" href="{html.escape(project["github_url"])}" target="_blank" rel="noopener noreferrer">GitHub Repository</a>'
            )
        cards.append(
            f"""        <article class="project-card">
            <img src="{html.escape(absolute_url(project["image"]))}" alt="{html.escape(project["title"])} project">
            <div>
{chr(10).join(details)}
            </div>
        </article>"""
        )
    return "\n".join(cards)


def replace_container(content: str, class_name: str, cards: str) -> str:
    opening_pattern = re.compile(
        rf'<div\b[^>]*class="[^"]*\b{class_name}\b[^"]*"[^>]*>',
        re.DOTALL,
    )
    opening_match = opening_pattern.search(content)
    if opening_match is None:
        raise RuntimeError(f"Could not find .{class_name} container")

    opening_tag = opening_match.group(0)
    if "data-static-content" not in opening_tag:
        opening_tag = opening_tag[:-1] + ' data-static-content="true">'

    tag_pattern = re.compile(r"<div\b[^>]*>|</div>", re.DOTALL)
    depth = 1
    closing_match = None
    for tag_match in tag_pattern.finditer(content, opening_match.end()):
        depth += 1 if tag_match.group(0).startswith("<div") else -1
        if depth == 0:
            closing_match = tag_match
            break
    if closing_match is None:
        raise RuntimeError(f"Could not find closing tag for .{class_name} container")

    return (
        content[: opening_match.start()]
        + opening_tag
        + "\n"
        + cards
        + "\n            "
        + closing_match.group(0)
        + content[closing_match.end() :]
    )


def main() -> None:
    with MAP_PATH.open(encoding="utf-8") as map_file:
        blog_map = json.load(map_file)

    blog_cards = render_blog_posts(blog_map.get("posts", []))
    project_cards = render_projects(blog_map.get("projects", []))
    for path in HTML_FILES:
        content = path.read_text(encoding="utf-8")
        if "blog-post-container" in content:
            content = replace_container(content, "blog-post-container", blog_cards)
        if "projects-container" in content:
            content = replace_container(content, "projects-container", project_cards)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"Generated static content in {path}")


if __name__ == "__main__":
    main()
