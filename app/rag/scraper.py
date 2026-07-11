"""
Why this file exists:
    The chatbot needs documents before it can perform Retrieval-Augmented
    Generation (RAG). Web scraping is one simple way to collect documents.

Responsibility:
    - Download a webpage.
    - Remove scripts, styles, and noisy HTML.
    - Extract clean readable text.
    - Save the text into data/documents/.

How it connects to the project:
    The /scrape API endpoint calls this module. The saved text can later be
    ingested into FAISS and Neo4j.
"""

from pathlib import Path
from typing import Dict

import requests
from bs4 import BeautifulSoup

from app.utils.config import settings
from app.utils.text import safe_filename


def scrape_webpage(url: str) -> Dict[str, str]:
    """Scrape a webpage and save clean text as a .txt document."""
    response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove elements that usually do not contain useful document text.
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else safe_filename(url)
    text = soup.get_text(separator="\n")

    # Clean empty lines and extra spaces.
    lines = [line.strip() for line in text.splitlines()]
    clean_text = "\n".join(line for line in lines if line)

    file_name = f"{safe_filename(title)}.txt"
    file_path: Path = settings.documents_dir / file_name

    file_path.write_text(
        f"Source URL: {url}\nTitle: {title}\n\n{clean_text}",
        encoding="utf-8",
    )

    return {
        "url": url,
        "title": title,
        "file_path": str(file_path),
        "characters": str(len(clean_text)),
    }
