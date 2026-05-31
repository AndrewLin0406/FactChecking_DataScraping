"""
Article Crawl on PolitiFact website.
"""

import requests, json, argparse, time
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

#============================================== HELPERS ==============================================

URLs = {
    "main": "https://www.politifact.com",
    "latest": "https://www.politifact.com/factchecks/list/",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Both Flop-O-Meter and Truth-O-Meter
verdicts = {
    "barely-true": "Mostly false",
    "half-true": "Half true",
    "mostly-true": "Mostly true",
    "true": "True",
    "false": "False",
    "pants-fire": "Pants on fire",

    "full-flop": "Full flop",
    "half-flip": "Half flop",
    "no-flop": "No flop"
}

#============================================== Function ==============================================

def parse_date(date):

    cleaned_date = (
        date
        .split("(")[0]
        .replace(".", "")
        .replace("Sept.", "Sep")
        .strip()
    )

    formats = [
        "%b %d, %Y",
        "%B %d, %Y"
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                cleaned_date,
                fmt
            )

        except ValueError:
            continue

    raise ValueError(
        f"Unknown date format: {date}"
    )

def getArticles(timestamp=None, limit=-1):

    done = False

    articles = []

    timestamp_datetime = None

    if timestamp is not None:

        timestamp_datetime = datetime.strptime(
            str(timestamp),
            "%Y%m%d"
        )

    page = 1

    while True:

        page_url = (
            f"{URLs['latest']}?page={page}"
        )

        # print(f"Collecting page {page}")

        response = requests.get(
            page_url,
            headers=HEADERS,
            timeout=(5, 30)
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        cards = soup.find_all(
            "article",
            class_="m-statement"
        )

        if not cards:
            print("No more articles.")
            break

        for card in cards:

            try:

                # =================================
                # URL
                # =================================

                quote_tag = card.find(
                    "div",
                    class_="m-statement__quote"
                )

                a_tag = (
                    quote_tag.find("a", href=True)
                    if quote_tag else None
                )

                article_url = (
                    urljoin(
                        URLs["main"],
                        a_tag["href"]
                    )
                    if a_tag else None
                )

                # =================================
                # CLAIM
                # =================================

                # claim = (
                #     quote_tag.get_text(
                #         " ",
                #         strip=True
                #     )
                #     if quote_tag else None
                # )

                # =================================
                # RATING
                # =================================

                # rating_tag = card.find(
                #     "img",
                #     class_="c-image__original"
                # )

                # rating = (
                #     rating_tag.get("alt")
                #     if rating_tag else None
                # )

                # =================================
                # SPEAKER
                # =================================

                speaker_tag = card.find(
                    "a",
                    class_="m-statement__name"
                )

                speaker = (
                    speaker_tag.get_text(
                        strip=True
                    )
                    if speaker_tag else None
                )

                # =================================
                # DATE
                # =================================

                footer_tag = card.find(
                    "footer",
                    class_="m-statement__footer"
                )

                date = None

                if footer_tag:

                    footer_text = footer_tag.get_text(
                        " ",
                        strip=True
                    )

                    # Example:
                    # By Caleb McCullough • May 27, 2026

                    if "•" in footer_text:

                        date = (
                            footer_text
                            .split("•")[-1]
                            .strip()
                        )

                # =================================
                # FILTER BY TIMESTAMP
                # =================================

                article_datetime = None

                if date:

                    article_datetime = parse_date(
                        date
                    )

                if (
                    timestamp_datetime is not None
                    and article_datetime is not None
                ):

                    if article_datetime < timestamp_datetime:
                        done = True
                        break

                # =================================
                # ARTICLE OBJECT
                # =================================

                article = {
                    # "claim": claim,
                    # "rating": rating,
                    "speaker": speaker,
                    "date": date,
                    "article_url": article_url
                }

                articles.append(article)

                #print(claim)

            except Exception as e:

                print("FAILED:", e)

        page += 1

        if (limit != -1 and page > limit) or done:
            break

        time.sleep(1)

    return articles

def scrape_article(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=(5, 30)
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    article_data = {
        "claim": None,
        "rating": None,
        "speaker": None,
        "author": [],
        "content": "",
        "sources": []
    }

    # ======================================
    # CLAIM
    # ======================================

    claim_tag = soup.find(
        "div",
        class_="m-statement__quote"
    )

    if claim_tag:

        article_data["claim"] = claim_tag.get_text(
            " ",
            strip=True
        )

    # ======================================
    # RATING
    # ======================================

    meter_div = soup.find(
        "div",
        class_="m-statement__meter"
    )

    if meter_div:

        rating_tag = meter_div.find(
            "img",
            alt=True
        )

        if rating_tag:

            article_data["rating"] = verdicts[rating_tag.get("alt")]

    # ======================================
    # SPEAKER
    # ======================================

    speaker_tag = soup.find(
        "a",
        class_="m-statement__name"
    )

    if speaker_tag:

        article_data["speaker"] = speaker_tag.get_text(
            " ",
            strip=True
        )

    # ======================================
    # AUTHORS + DATE
    # ======================================

    author_blocks = soup.find_all(
        "div",
        class_="m-author__content"
    )

    for block in author_blocks:

        author_link = block.find("a")

        date_tag = block.find(
            "span",
            class_="m-author__date"
        )

        author_name = (
            author_link.get_text(
                " ",
                strip=True
            )
            if author_link else None
        )

        if author_name:
            article_data["author"].append(author_name)

    # ======================================
    # CONTENT
    # ======================================

    content = {
        "if_your_time_is_short": [],
        "article_content": [],
        "our_ruling": []
    }

    body = soup.find(
        "article",
        class_="m-textblock"
    )

    print(body)

    if body:

        in_ruling = False

        # ==================================
        # ARTICLE CONTENT + OUR RULING
        # ==================================

        for element in body.find_all(["p", "h2", "h3"]):

            print("TAG:", getattr(element, "name", None))

            if not hasattr(element, "name"):
                continue

            if (
                element.name in ["h2", "h3"]
                and "our ruling" in element.get_text().lower()
            ):
                print("FOUND RULING")
                in_ruling = True
                continue

            if element.name != "p":
                continue

            text = element.get_text(" ", strip=True)

            print("PARAGRAPH:", text[:50])

            if in_ruling:
                print("APPEND RULING")
                content["our_ruling"].append(text)
            else:
                print("APPEND CONTENT")
                content["article_content"].append(text)

        # ==================================
        # IF YOUR TIME IS SHORT
        # ==================================

        short_section = soup.find(
            "div",
            class_="short-on-time"
        )

        if short_section:

            for li in short_section.find_all("li"):

                text = li.get_text(
                    " ",
                    strip=True
                )

                if text:

                    content[
                        "if_your_time_is_short"
                    ].append(text)

    article_data["content"] = content

    # ======================================
    # SOURCES
    # ======================================

    sources_section = soup.find(
        "section",
        id="sources"
    )

    sources = []

    if sources_section:

        source_paragraphs = sources_section.find_all("p")

        for p in source_paragraphs:

            source = {
                "raw_text": p.get_text(
                    " ",
                    strip=True
                ),
                "links": []
            }

            for a in p.find_all("a", href=True):
                source["links"].append(a["href"])

            sources.append(source)

    article_data["sources"] = sources

    return article_data

def getData(outputDirectory, category, timeStamp, limit, dataset_name="politifact_articles.json"):
    outputDirectory.mkdir(
        parents=True,
        exist_ok=True
    )

    articles = getArticles(timeStamp, limit=limit)
    outputFile = outputDirectory / dataset_name

    print("Finished Collecting The Articles.")

    filtered_articles = []

    for article in articles:

        article_data = scrape_article(
            article["article_url"]
        )

        # skip non-English articles
        if article_data is None:
            continue

        article["article_data"] = article_data

        filtered_articles.append(article)
    
    print("Finished Scraping The Articles.")

    with open(outputFile, "w", encoding="utf-8") as f:
        json.dump(
            filtered_articles,
            f,
            ensure_ascii=False,
            indent=4
        )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract the articles from the Snopes.com web"
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("DATASET"),
        help="Root directory containing extracted datasets.",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="fact-check",
        help="Category of articles (ALL, latest, trending, politics, entertainment).",
    )
    parser.add_argument(
        "--time-stamp",
        type=int,
        default=None,
        help="Format : (YYYYMMDD), Leave None if do not want to filter by time"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Maximum number of pages to crawl",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    output_root = args.output_dir
    category_name = args.category
    time_stamp = args.time_stamp
    limit = args.limit

    getData(output_root, category_name, time_stamp, limit)

if __name__ == "__main__":
    main()