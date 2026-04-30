import json
from collections import Counter
from pathlib import Path


DATASET_PATH = Path("data/articles.json")
SHORT_CONTENT_THRESHOLD = 1000
EXCESSIVE_WHITESPACE_RUN = 4


def load_articles(path: Path = DATASET_PATH) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Dataset must be a list of article dictionaries")

    return data


def content_length(article: dict[str, str]) -> int:
    return len(article.get("content", ""))


def has_repeated_lines(content: str) -> bool:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    counts = Counter(lines)

    return any(count > 1 for count in counts.values())


def has_excessive_whitespace(content: str) -> bool:
    return (
        "\n" * EXCESSIVE_WHITESPACE_RUN in content
        or " " * EXCESSIVE_WHITESPACE_RUN in content
        or "\t" in content
    )


def count_duplicates(values: list[str]) -> int:
    counts = Counter(value for value in values if value)
    return sum(count - 1 for count in counts.values() if count > 1)


def print_sample_articles(articles: list[dict[str, str]]) -> None:
    print("Sample Articles")
    print("=" * 60)

    for index, article in enumerate(articles[:3], start=1):
        title = article.get("title", "")
        content = article.get("content", "")
        preview = content[:300].replace("\n", " ")

        print(f"{index}. {title}")
        print(f"   Content length: {len(content)} chars")
        print(f"   Preview: {preview}")
        print()


def generate_report(articles: list[dict[str, str]]) -> None:
    lengths = [content_length(article) for article in articles]
    total_articles = len(articles)

    min_length = min(lengths) if lengths else 0
    max_length = max(lengths) if lengths else 0
    average_length = sum(lengths) / total_articles if total_articles else 0

    short_articles = [
        article for article in articles
        if content_length(article) < SHORT_CONTENT_THRESHOLD
    ]
    repeated_line_count = sum(
        1 for article in articles
        if has_repeated_lines(article.get("content", ""))
    )
    excessive_whitespace_count = sum(
        1 for article in articles
        if has_excessive_whitespace(article.get("content", ""))
    )

    duplicate_title_count = count_duplicates([
        article.get("title", "").strip()
        for article in articles
    ])
    duplicate_content_count = count_duplicates([
        article.get("content", "").strip()
        for article in articles
    ])

    print()
    print("Dataset Quality Report")
    print("=" * 60)
    print(f"Total articles: {total_articles}")
    print(f"Min content length: {min_length} chars")
    print(f"Max content length: {max_length} chars")
    print(f"Average content length: {average_length:.2f} chars")
    print(f"Empty or very short articles (< {SHORT_CONTENT_THRESHOLD} chars): {len(short_articles)}")
    print()

    print("Content Quality Checks")
    print("=" * 60)
    print(f"Articles with repeated lines: {repeated_line_count}")
    print(f"Articles with excessive whitespace: {excessive_whitespace_count}")
    print(f"Suspiciously short articles: {len(short_articles)}")
    print()

    print("Deduplication Check")
    print("=" * 60)
    print(f"Duplicate titles: {duplicate_title_count}")
    print(f"Duplicate content entries: {duplicate_content_count}")
    print()

    print_sample_articles(articles)


if __name__ == "__main__":
    articles = load_articles()
    generate_report(articles)
