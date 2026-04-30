import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


INDEX_URL = "https://www.paulgraham.com/articles.html"
BASE_URL = "https://www.paulgraham.com/"
OUTPUT_PATH = Path("data/articles.json")
TIMEOUT_SECONDS = 20
MIN_CONTENT_LENGTH = 200
EXCLUDED_PATHS = {
    "/articles.html",
    "/index.html",
    "/rss.html",
    "/rss",
}


def _clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n\n".join(lines)


def _is_valid_article_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path

    return (
        parsed.netloc == "www.paulgraham.com"
        and path.endswith(".html")
        and path not in EXCLUDED_PATHS
        and "/" not in path.strip("/")
    )


def get_article_links(index_url: str = INDEX_URL) -> list[str]:
    response = requests.get(index_url, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    seen = set()

    for anchor in soup.find_all("a", href=True):
        url = urljoin(BASE_URL, anchor["href"])

        if not _is_valid_article_url(url) or url in seen:
            continue

        seen.add(url)
        links.append(url)

    return links


def extract_article(url: str) -> dict[str, str] | None:
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Skipping failed page: {url} ({exc})")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""
    body = soup.find("body")
    if body is None:
        print(f"Skipping page without body: {url}")
        return None

    for tag in body(["script", "style", "nav"]):
        tag.decompose()

    content = _clean_text(body.get_text(separator="\n"))

    if not title or not content:
        print(f"Skipping page without usable content: {url}")
        return None

    if len(content) < 1000:
        print(f"Skipping short/non-essay page: {url}")
        return None

    return {
        "title": title,
        "url": url,
        "content": content,
    }


def scrape_all(index_url: str = INDEX_URL) -> list[dict[str, str]]:
    articles = []

    try:
        links = get_article_links(index_url)
    except requests.RequestException as exc:
        print(f"Failed to fetch article index: {index_url} ({exc})")
        return articles

    for url in links:
        print(f"Scraping: {url}")
        article = extract_article(url)
        if article is not None:
            articles.append(article)

    print(f"Total valid articles: {len(articles)}")
    return articles


if __name__ == "__main__":
    scraped_articles = scrape_all()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(scraped_articles, file, ensure_ascii=False, indent=2)

    print(f"Saved {len(scraped_articles)} articles to {OUTPUT_PATH}")
