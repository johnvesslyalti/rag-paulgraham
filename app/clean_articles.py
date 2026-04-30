import json
from pathlib import Path


ARTICLES_PATH = Path("data/articles.json")


def remove_duplicate_lines(text: str) -> str:
    seen = set()
    cleaned_lines = []

    for line in text.splitlines():
        if line and line in seen:
            continue

        if line:
            seen.add(line)

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def clean_articles(articles: list[dict[str, str]]) -> list[dict[str, str]]:
    cleaned_articles = []

    for article in articles:
        cleaned_articles.append(
            {
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "content": remove_duplicate_lines(article.get("content", "")),
            }
        )

    return cleaned_articles


def main() -> None:
    with ARTICLES_PATH.open("r", encoding="utf-8") as file:
        articles = json.load(file)

    cleaned_articles = clean_articles(articles)

    with ARTICLES_PATH.open("w", encoding="utf-8") as file:
        json.dump(cleaned_articles, file, ensure_ascii=False, indent=2)

    print(f"Cleaned and replaced {ARTICLES_PATH}")
    print(f"Total articles: {len(cleaned_articles)}")


if __name__ == "__main__":
    main()
