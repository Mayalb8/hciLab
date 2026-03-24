import requests
from bs4 import BeautifulSoup
import re

JACOB_URL = "https://www.cs.tufts.edu/~jacob/papers/"
LAB_FILE = "publications.html"

def normalize_title(t):
    """Normalize titles for deduplication."""
    return re.sub(r"\s+", " ", t).strip().lower()

def scrape_jacob():
    """Scrape publications from Jacob's page."""
    html = requests.get(JACOB_URL).text
    soup = BeautifulSoup(html, "html.parser")

    pubs = []
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if not text or len(text) < 20:
            continue

        # Extract PDF link if present
        pdf = None
        link = p.find("a", href=True)
        if link and link["href"].lower().endswith(".pdf"):
            href = link["href"]
            if href.startswith("http"):
                pdf = href
            else:
                pdf = JACOB_URL + href

        pubs.append({
            "raw": text,
            "title": text.split(".")[0],
            "pdf": pdf
        })

    return pubs

def scrape_lab():
    """Scrape existing publications from the lab page."""
    with open(LAB_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    existing_titles = set()

    for li in soup.select("li"):
        text = li.get_text(" ", strip=True)
        if text:
            title = text.split(".")[0]
            existing_titles.add(normalize_title(title))

    return soup, existing_titles

def format_pub(pub):
    """Format a publication as an <li> entry."""
    if pub["pdf"]:
        return f'<li><a href="{pub["pdf"]}">{pub["raw"]}</a></li>'
    else:
        return f"<li>{pub['raw']}</li>"

def main():
    jacob_pubs = scrape_jacob()
    soup, existing = scrape_lab()

    new_items = []
    for pub in jacob_pubs:
        fp = normalize_title(pub["title"])
        if fp not in existing:
            new_items.append(pub)

    if not new_items:
        print("No new publications found.")
        return

    print(f"Found {len(new_items)} new publications.")

    # Insert into the <ul> on your page
    ul = soup.find("ul")
    for pub in new_items:
        li_html = format_pub(pub)
        ul.append(BeautifulSoup(li_html, "html.parser"))

    # Write updated HTML
    with open(LAB_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print("publications.html updated.")

if __name__ == "__main__":
    main()
