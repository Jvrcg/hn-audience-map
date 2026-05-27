"""
HN Audience Map - Compute Overlap Matrix
For each pair of domains, computes how many commenters they share.
Output: data/overlap_matrix.json
"""

import json
from pathlib import Path
from itertools import combinations

DATA_DIR = Path("data")
INPUT_FILE = DATA_DIR / "hn_raw_data.json"
OUTPUT_FILE = DATA_DIR / "overlap_matrix.json"


def main():
    with open(INPUT_FILE) as f:
        data = json.load(f)

    # Convert commenter lists to sets for fast intersection
    commenter_sets = {
        domain: set(info["commenters"])
        for domain, info in data.items()
    }

    domains = list(commenter_sets.keys())
    print(f"Computing overlap for {len(domains)} domains "
          f"({len(domains) * (len(domains) - 1) // 2} pairs)\n")

    # Compute pairwise overlap
    edges = []
    for d1, d2 in combinations(domains, 2):
        set1 = commenter_sets[d1]
        set2 = commenter_sets[d2]
        shared = set1 & set2
        if len(shared) == 0:
            continue

        # Jaccard similarity: shared / total unique across both
        union = set1 | set2
        jaccard = len(shared) / len(union) if union else 0

        # Overlap coefficient: shared / smaller set
        # (better when one domain is much larger than the other)
        smaller = min(len(set1), len(set2))
        overlap_coef = len(shared) / smaller if smaller else 0

        edges.append({
            "source": d1,
            "target": d2,
            "shared_commenters": len(shared),
            "jaccard": round(jaccard, 4),
            "overlap_coefficient": round(overlap_coef, 4),
            "source_size": len(set1),
            "target_size": len(set2),
        })

    # Sort by shared commenters (most overlap first)
    edges.sort(key=lambda x: x["shared_commenters"], reverse=True)

    # Node metadata
    nodes = []
    for domain in domains:
        nodes.append({
            "domain": domain,
            "story_count": data[domain]["story_count"],
            "commenter_count": data[domain]["commenter_count"],
        })

    output = {
        "nodes": nodes,
        "edges": edges,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    # Print top 15 pairs
    print(f"Top 15 audience overlaps (by shared commenters):\n")
    print(f"{'Source':<20} {'Target':<20} {'Shared':>8} {'Jaccard':>10} {'OverlapCoef':>12}")
    print("-" * 75)
    for edge in edges[:15]:
        print(f"{edge['source']:<20} {edge['target']:<20} "
              f"{edge['shared_commenters']:>8} "
              f"{edge['jaccard']:>10.4f} "
              f"{edge['overlap_coefficient']:>12.4f}")

    print(f"\nTotal pairs with overlap: {len(edges)}")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()