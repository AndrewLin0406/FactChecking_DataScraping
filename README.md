# Fact-Checking Article Crawlers

This project contains two web crawlers for collecting fact-check articles from:

* Snopes
* PolitiFact

The crawlers extract:

* Article metadata
* Claims
* Verdict labels
* Article content
* Sources / references
* Hyperlinks

The extracted articles are saved as structured JSON datasets for downstream NLP and fact-checking experiments.

---

# Features

## Snopes Crawler

Extracts:

* Title
* Author
* Date
* Byline
* Claim reviewed
* Verdict / rating
* Article content
* Sources section
* Source hyperlinks

Supports:

* Pagination crawling
* Timestamp filtering
* Category filtering

---

## PolitiFact Crawler

Extracts:

* Speaker
* Claim
* Verdict label
* Author
* Date
* "If Your Time Is Short"
* Full article content
* "Our Ruling"
* Sources section
* Source hyperlinks

Supports:

* Pagination crawling
* Timestamp filtering
* Automatic English-only filtering

---

# Installation

Install dependencies:

```bash
pip install requests beautifulsoup4
```

---

# Project Structure

```text
PROJECT/
│
├── SnopesCrawl.py
├── PolitifactCrawl.py
├── DATASET/
│   ├── snopes_articles.json
│   └── politifact_articles.json
└── README.md
```

---

# Running the Crawlers

## Snopes

Each page contains 20 articles.

```bash
python SnopesCrawl.py
```

Example with timestamp filtering:

Each page contains 30 articles

```bash
python SnopesCrawl.py --time-stamp 20250101
```

Example with page limit:

```bash
python SnopesCrawl.py --limit 50
```

---

## PolitiFact

```bash
python PolitifactCrawl.py
```

Example with timestamp filtering:

```bash
python PolitifactCrawl.py --time-stamp 20250101
```

Example with page limit:

```bash
python PolitifactCrawl.py --limit 50
```

---

# Command Line Arguments

| Argument       | Description                               |
| -------------- | ----------------------------------------- |
| `--output-dir` | Output dataset directory                  |
| `--time-stamp` | Filter articles after a date (`YYYYMMDD`) |
| `--limit`      | Maximum number of pages to crawl          |
| `--category`   | Article category (used mainly for Snopes) |

---

## PolitiFact Output Format

Example article structure:

```json
{
    "speaker": "TikTok posts",
    "date": "May 28, 2026",
    "article_url": "...",
    "article_data": {
        "claim": "...",
        "rating": "False",
        "author": "Maria Briceño",
        "content": {
            "if_your_time_is_short": [],
            "article_content": [],
            "our_ruling": []
        },
        "sources": [
            {
                "raw_text": "...",
                "links": "https://..."
            }
        ]
    }
}
```
## Snopes Dataset Format

Example article structure:

```json
{
    "title": "Thieves aren't using perfume to knock out victims, despite persistent rumors",
    "article_url": "https://www.snopes.com/fact-check/thieves-perfume-shock-victims/",
    "author": "Joey Esposito",
    "date": "May 28, 2026",
    "byline": "Versions of this longstanding urban legend have lurked on the web since the 1990s.",
    "article_data": {
        "claim": "Thieves operating in public places are using drug-filled perfume bottles to render their victims unconscious.",
        "rating": "False",
        "author": "Joey Esposito",
        "datePublished": "2026-05-28T08:00:06Z",
        "content": "Full article text...",
        "sources": [
            "CDC Health-Related Hoaxes & Rumors. https://webharvest.gov/...",
            "Drugs@FDA: FDA-Approved Drugs. https://www.accessdata.fda.gov/...",
            "\"Hydroxyzine (Oral Route).\" Mayo Clinic, https://www.mayoclinic.org/..."
        ]
    }
}
```

---

# Timestamp Filtering

The crawlers support filtering articles newer than a given date.

Example:

```bash
python PolitifactCrawl.py --time-stamp 20250101
```

This collects only articles published after:

```text
2025-01-01
```
