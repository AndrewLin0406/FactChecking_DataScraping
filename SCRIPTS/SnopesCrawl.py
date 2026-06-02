"""
Article Crawl on snopes.com website.
"""

import requests, json, time, argparse
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

#============================================== HELPERS ==============================================

URLs = {
    "main": "https://www.snopes.com/",
    "fact-check": "https://www.snopes.com/fact-check/",
    "trending": "https://www.snopes.com/top/",
    "latest": "https://www.snopes.com/top/",
    "politics": "https://www.snopes.com/category/politics/",
    "entertainment": "https://www.snopes.com/category/Entertainment/"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

#============================================== Function ==============================================

from datetime import datetime

def parse_date(date):

    cleaned_date = (
        date
        .split("(")[0]
        .replace(".", "")
        .replace("Sept", "Sep")
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

def getArticles(URL_category="fact-check", timestamp=None, limit=-1):

    articles = []
    page = 1

    done = False

    timestamp_datetime = None

    if timestamp is not None:

        timestamp_datetime = datetime.strptime(
            str(timestamp),
            "%Y%m%d"
        )

    while True:

        if page == 1:
            page_url = URLs[URL_category]
        else:
            page_url = f"{URLs[URL_category]}?pagenum={page}"

        # print(
        #     "-" * 10 +
        #     f" Collecting Articles from Page {page} " +
        #     "-" * 10,
        #     end="\n\n"
        # )

        html = requests.get(page_url).text
        soup = BeautifulSoup(html, "html.parser")

        article_wrappers = soup.find_all(
            "div",
            class_="article_wrapper"
        )

        if not article_wrappers:
            print("No more articles found.")
            break

        for wrapper in article_wrappers:

            try:

                # URL
                a_tag = wrapper.find(
                    "a",
                    class_="outer_article_link_wrapper"
                )

                article_url = a_tag["href"]
                article_url = article_url.replace(".com//", ".com/")

                # TITLE
                title_tag = wrapper.find(
                    "h3",
                    class_="article_title"
                )

                title = title_tag.get_text(strip=True)

                # AUTHOR
                author_tag = wrapper.find(
                    "span",
                    class_="author_name"
                )

                author = (
                    author_tag.get_text(strip=True)
                    if author_tag else None
                )

                # DATE
                date_tag = wrapper.find(
                    "span",
                    class_="article_date"
                )

                date = (
                    date_tag.get_text(strip=True)
                    if date_tag else None
                )
                
                article_datetime = None

                if date:
                    article_datetime = parse_date(date)

                # BYLINE
                byline_tag = wrapper.find(
                    "span",
                    class_="article_byline"
                )

                byline = (
                    byline_tag.get_text(" ", strip=True)
                    if byline_tag else None
                )

                # SINGLE ARTICLE OBJECT
                article = {
                    "title": title,
                    "article_url": article_url,
                    "author": author,
                    "date": date,
                    "byline": byline
                }

                if (timestamp_datetime is not None and article_datetime is not None):
                    print(article_datetime, timestamp_datetime)
                    if article_datetime < timestamp_datetime:
                        print("2")
                        done = True
                        break   

                articles.append(article)

            except Exception as e:
                print("Failed:", e)

        page += 1

        if (limit != -1 and page > limit) or done:
            break
    
    return articles

def scrape_article(url):

    html = requests.get(url, headers=HEADERS).text
    soup = BeautifulSoup(html, "html.parser")

    article_data = {
        "claim": None,
        "rating": None,
        "author": None,
        "datePublished": None,
        "content": "",
        "sources": []
    }

    # ==========================================
    # PARSE JSON-LD
    # ==========================================

    scripts = soup.find_all(
        "script",
        type="application/ld+json"
    )

    for script in scripts:

        try:
            data = json.loads(script.string)

            # ----------------------------
            # ClaimReview block
            # ----------------------------
            if data.get("@type") == "ClaimReview":

                article_data["claim"] = data.get(
                    "claimReviewed"
                )

                review = data.get("reviewRating", {})

                article_data["rating"] = review.get(
                    "alternateName"
                )

            # ----------------------------
            # Article block
            # ----------------------------
            elif data.get("@type") == "Article":
                article_data["datePublished"] = data.get(
                    "datePublished"
                )

                author = data.get("author", {})

                article_data["author"] = author.get(
                    "name"
                )

        except Exception:
            pass

    # ==========================================
    # ARTICLE CONTENT
    # ==========================================

    article_body = soup.find("article")

    paragraphs = []

    if article_body:

        for p in article_body.find_all("p"):

            text = p.get_text(" ", strip=True)

            if text:
                paragraphs.append(text)

    if not paragraphs:
        print(f"EMPTY ARTICLE: {url}")
        return None

    if "about this rating" in paragraphs[0].lower():
        paragraphs.pop(0)

    article_data["content"] = "\n\n".join(paragraphs)

    # ==========================================
    # HYPERLINK SOURCES : PROBABLY DONT WANT THIS
    # ==========================================

    # links = []

    # if article_body:

    #     for a in article_body.find_all("a", href=True):

    #         href = a["href"]
    #         text = a.get_text(" ", strip=True)

    #         links.append({
    #             "text": text,
    #             "url": href
    #         })

    # article_data["hyper_links"] = links[1:]

    # ==========================================
    # SOURCES / REFERENCES
    # ==========================================

    sources = []

    sources_div = soup.find("div", id="sources_rows")

    if sources_div:

        for p in sources_div.find_all("p"):

            source = []

            sources.append(p.get_text(
                " ",
                strip=True
            ))

    article_data["sources"] = sources

    return article_data

def getData(outputDirectory, category, timeStamp, limit, dataset_name="snopes_articles.json"):
    outputDirectory.mkdir(
        parents=True,
        exist_ok=True
    )

    articles = getArticles(category, timeStamp, limit=limit)
    outputFile = outputDirectory / dataset_name

    print("Finished Collecting The Articles")

    for article in articles:
        article_data = scrape_article(article["article_url"])
        article["article_data"] = article_data

    print(f"Finished Scraping The Articles, Sraped {len(articles)} Articles")
    
    with open(outputFile, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

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
        default=300,
        help="Maximum number of pages to crawl (-1 : no limit)",
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
