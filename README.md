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

```bash
python SnopesCrawl.py
```

Example with timestamp filtering:

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

# Output Format

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

---

# Notes

* Some websites may change their HTML structure over time.
* Crawling large numbers of pages may take significant time.
* A delay is included between requests to reduce server load.
* PolitiFact multilingual articles are filtered to English-only articles.

#
