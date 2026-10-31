#!/usr/bin/env python3
"""Generate the site's RSS feed from blog/blog-map.json."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "blog" / "blog-map.json"
FEED_PATH = ROOT / "feed.xml"


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def rss_date(value: str) -> str:
    return parse_date(value).strftime("%a, %d %b %Y 00:00:00 +0000")


def site_url_from_environment() -> str:
    repository = os.environ.get("GITHUB_REPOSITORY", "db-vol-1/portfolio")
    owner, _, name = repository.partition("/")
    return f"https://{owner}.github.io/{name}"


def build_feed(site_url: str) -> ElementTree.Element:
    with MAP_PATH.open(encoding="utf-8") as map_file:
        blog_map = json.load(map_file)

    site_url = site_url.rstrip("/") + "/"
    channel = ElementTree.Element(
        "channel",
        {
            "xmlns:atom": "http://www.w3.org/2005/Atom",
        },
    )
    ElementTree.SubElement(channel, "title").text = "db_vol_1 Blog"
    ElementTree.SubElement(channel, "link").text = site_url
    ElementTree.SubElement(channel, "description").text = (
        "Articles from the db_vol_1 blog."
    )
    ElementTree.SubElement(channel, "language").text = "en-us"
    ElementTree.SubElement(
        channel,
        "atom:link",
        {
            "href": urljoin(site_url, "feed.xml"),
            "rel": "self",
            "type": "application/rss+xml",
        },
    )

    posts = sorted(
        blog_map.get("posts", []),
        key=lambda post: post["date"],
        reverse=True,
    )
    for post in posts:
        relative_url = post["url"].lstrip("./")
        post_path = ROOT / relative_url
        if not post_path.is_file():
            print(
                f"Warning: skipping {post['title']!r}; "
                f"post file does not exist: {relative_url}"
            )
            continue

        link = urljoin(site_url, relative_url)
        item = ElementTree.SubElement(channel, "item")
        ElementTree.SubElement(item, "title").text = post["title"]
        ElementTree.SubElement(item, "link").text = link
        ElementTree.SubElement(item, "guid", {"isPermaLink": "true"}).text = link
        ElementTree.SubElement(item, "pubDate").text = rss_date(post["date"])
        ElementTree.SubElement(item, "description").text = post["description"]
        for tag in post.get("tags", []):
            ElementTree.SubElement(item, "category").text = tag

    return channel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-url", default=site_url_from_environment())
    args = parser.parse_args()

    feed = ElementTree.Element("rss", {"version": "2.0"})
    feed.append(build_feed(args.site_url))
    tree = ElementTree.ElementTree(feed)
    ElementTree.indent(tree, space="    ")
    tree.write(FEED_PATH, encoding="utf-8", xml_declaration=True)
    print(f"Generated {FEED_PATH}")


if __name__ == "__main__":
    main()
