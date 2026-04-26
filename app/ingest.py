import requests
from bs4 import BeautifulSoup

URL = "https://www.paulgraham.com/brandage.html"

def fetch_and_clean():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract full body text
    body = soup.find("body")
    text = body.get_text(separator="\n")

    # Clean extra whitespace
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    clean_text = "\n\n".join(lines)

    # Save to file
    with open("data/essay.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)

    print("✅ Data saved to data/essay.txt")


if __name__ == "__main__":
    fetch_and_clean()