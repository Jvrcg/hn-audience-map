"""
HN Audience Map - Data Fetcher v4
Fix: use restrictSearchableAttributes to search URL field directly,
avoiding false positives from Algolia's full-text query.
"""

import requests
import json
import time
from urllib.parse import urlparse
from pathlib import Path

DOMAINS = [
  # Ring 1: Direct competitors
    "baseten.com",
    "modal.com",
    "replicate.com",
    "runpod.io",
    "together.ai",
    "anyscale.com",
    "huggingface.co",
    "fireworks.ai",
    # Ring 2: Adjacent tooling
    "langchain.com",
    "llamaindex.ai",
    "wandb.ai",
    "pinecone.io",
    "weaviate.io",
    "trychroma.com",
    "mlflow.org",
    "bentoml.com",
    "ray.io",
    # Ring 3: Foundation models
    "openai.com",
    "anthropic.com",
    "mistral.ai",
    "cohere.com",
    "meta.com",
    # Ring 4: Broader infra
    "aws.amazon.com",
    "cloud.google.com",
    "vercel.com",
    "supabase.com",
    "nvidia.com",
    "databricks.com",
    "snowflake.com",
    "microsoft.com",
    "cloudflare.com",
]

MONTHS_BACK = 12
SECONDS_PER_DAY = 86400
CUTOFF_TIMESTAMP = int(time.time()) - (MONTHS_BACK * 30 * SECONDS_PER_DAY)

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"
SLEEP_BETWEEN_REQUESTS = 1

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


def url_matches_domain(url, domain):
    if not url:
        return False
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return False
    return host == domain or host.endswith("." + domain)


def fetch_stories_for_domain(domain):
    stories = []
    seen_urls = set()
    page = 0
    hits_per_page = 100
    consecutive_empty_pages = 0
    MAX_EMPTY_PAGES = 3

    while True:
        params = {
            "tags": "story",
            "numericFilters": f"created_at_i>{CUTOFF_TIMESTAMP}",
            "query": domain,
            "restrictSearchableAttributes": "url",
            "hitsPerPage": hits_per_page,
            "page": page,
        }

        try:
            response = requests.get(HN_SEARCH_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"  Request failed for {domain} page {page}: {e}")
            break

        hits = data.get("hits", [])
        if not hits:
            break

        matches_this_page = 0
        for hit in hits:
            url = hit.get("url", "") or ""
            if url_matches_domain(url, domain):
                url_lower = url.lower()
                if url_lower not in seen_urls:
                    seen_urls.add(url_lower)
                    stories.append({
                        "story_id": hit.get("objectID"),
                        "title": hit.get("title"),
                        "url": url,
                        "author": hit.get("author"),
                        "points": hit.get("points", 0),
                        "created_at": hit.get("created_at"),
                    })
                    matches_this_page += 1

        if matches_this_page == 0:
            consecutive_empty_pages += 1
            if consecutive_empty_pages >= MAX_EMPTY_PAGES:
                break
        else:
            consecutive_empty_pages = 0

        if len(hits) < hits_per_page:
            break

        page += 1
        time.sleep(SLEEP_BETWEEN_REQUESTS)

        if page > 30:
            break

    return stories


def fetch_commenters_for_story(story_id):
    url = f"https://hn.algolia.com/api/v1/items/{story_id}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"    Failed to fetch story {story_id}: {e}")
        return set()

    commenters = set()

    def walk(node):
        if not node:
            return
        author = node.get("author")
        if author:
            commenters.add(author)
        for child in node.get("children", []):
            walk(child)

    walk(data)
    story_author = data.get("author")
    commenters.discard(story_author)
    return commenters


def main():
    print(f"Starting HN data pull for {len(DOMAINS)} domains")
    print(f"Time window: last {MONTHS_BACK} months\n")

    results = {}

    for i, domain in enumerate(DOMAINS, 1):
        print(f"[{i}/{len(DOMAINS)}] {domain}")

        stories = fetch_stories_for_domain(domain)
        print(f"  Found {len(stories)} unique stories")

        all_commenters = set()
        for j, story in enumerate(stories, 1):
            commenters = fetch_commenters_for_story(story["story_id"])
            all_commenters.update(commenters)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

            if j % 10 == 0:
                print(f"    Processed {j}/{len(stories)} stories, "
                      f"{len(all_commenters)} unique commenters so far")

        results[domain] = {
            "story_count": len(stories),
            "commenter_count": len(all_commenters),
            "commenters": sorted(all_commenters),
            "stories": stories,
        }

        print(f"  Done: {len(all_commenters)} unique commenters total\n")

    output_file = OUTPUT_DIR / "hn_raw_data.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved raw data to {output_file}")
    print(f"\nSummary:")
    for domain, data in results.items():
        print(f"  {domain}: {data['story_count']} stories, "
              f"{data['commenter_count']} commenters")


if __name__ == "__main__":
    main()