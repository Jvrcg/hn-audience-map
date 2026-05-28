"""
HN Audience Map - Static Visualization (focus + context)
Full network in gray background, Baseten cluster surfaced in color.
"""

import json
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

DATA_DIR = Path("data")
OVERLAP_FILE = DATA_DIR / "overlap_matrix.json"
OUTPUT_FILE = "hn_audience_map.png"

# Domains in Baseten's competitive cluster (Ring 1 + 2) — surfaced in color
FOCUS_DOMAINS = {
    "baseten.com", "modal.com", "replicate.com", "runpod.io",
    "together.ai", "anyscale.com", "huggingface.co", "fireworks.ai",
    "langchain.com", "llamaindex.ai", "wandb.ai", "pinecone.io",
    "weaviate.io", "trychroma.com", "mlflow.org", "bentoml.com", "ray.io",
}

# Use overlap_coefficient for edges (better when domain sizes vary widely)
MIN_OVERLAP_COEF = 0.10  # only draw edges above this threshold


def main():
    with open(OVERLAP_FILE) as f:
        data = json.load(f)

    G = nx.Graph()

    # Add nodes with their commenter count as size attribute
    for node in data["nodes"]:
        G.add_node(node["domain"], size=node["commenter_count"])

    # Add edges above threshold
    for edge in data["edges"]:
        if edge["overlap_coefficient"] >= MIN_OVERLAP_COEF:
            G.add_edge(
                edge["source"],
                edge["target"],
                weight=edge["overlap_coefficient"],
                shared=edge["shared_commenters"],
            )

    # Remove isolated nodes (no edges above threshold)
    G.remove_nodes_from(list(nx.isolates(G)))

    # Layout
    pos = nx.spring_layout(G, k=0.6, iterations=50, seed=42)

    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_facecolor("#0d1117")
    fig.patch.set_facecolor("#0d1117")

    # Split nodes into focus vs context
    focus_nodes = [n for n in G.nodes() if n in FOCUS_DOMAINS]
    context_nodes = [n for n in G.nodes() if n not in FOCUS_DOMAINS]

    # Node sizes scaled by commenter count
    def node_size(n):
        return 80 + (G.nodes[n]["size"] ** 0.5) * 12

    # Draw context edges (faint)
    context_edges = [
        (u, v) for u, v in G.edges()
        if u not in FOCUS_DOMAINS or v not in FOCUS_DOMAINS
    ]
    nx.draw_networkx_edges(
        G, pos, edgelist=context_edges,
        edge_color="#30363d", width=0.5, alpha=0.4, ax=ax,
    )

    # Draw focus edges (bright)
    focus_edges = [
        (u, v) for u, v in G.edges()
        if u in FOCUS_DOMAINS and v in FOCUS_DOMAINS
    ]
    nx.draw_networkx_edges(
        G, pos, edgelist=focus_edges,
        edge_color="#58a6ff", width=1.5, alpha=0.8, ax=ax,
    )

    # Draw context nodes (grayed out)
    nx.draw_networkx_nodes(
        G, pos, nodelist=context_nodes,
        node_size=[node_size(n) for n in context_nodes],
        node_color="#484f58", alpha=0.5, ax=ax,
    )

    # Draw focus nodes (colored)
    nx.draw_networkx_nodes(
        G, pos, nodelist=focus_nodes,
        node_size=[node_size(n) for n in focus_nodes],
        node_color="#58a6ff", alpha=0.95, ax=ax,
    )

    # Highlight Baseten specifically
    if "baseten.com" in G.nodes():
        nx.draw_networkx_nodes(
            G, pos, nodelist=["baseten.com"],
            node_size=[node_size("baseten.com") + 200],
            node_color="#f78166", alpha=1.0, ax=ax,
        )

    # Labels — focus nodes get bright labels, context gets faint
    focus_labels = {n: n.replace(".com", "").replace(".ai", "").replace(".io", "").replace(".org", "").replace(".co", "") for n in focus_nodes}
    context_labels = {n: n.replace(".com", "").replace(".ai", "").replace(".io", "").replace(".org", "").replace(".co", "") for n in context_nodes}

    nx.draw_networkx_labels(
        G, pos, labels=context_labels,
        font_size=8, font_color="#8b949e", ax=ax,
    )
    nx.draw_networkx_labels(
        G, pos, labels=focus_labels,
        font_size=10, font_color="#ffffff", font_weight="bold", ax=ax,
    )

    ax.set_title(
        "HN Audience Overlap Map — Where Baseten Operates in the AI Conversation",
        color="#ffffff", fontsize=16, pad=20,
    )
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150, facecolor="#0d1117", bbox_inches="tight")
    print(f"Saved visualization to {OUTPUT_FILE}")
    print(f"Nodes drawn: {G.number_of_nodes()}")
    print(f"Edges drawn: {G.number_of_edges()}")
    print(f"Focus nodes: {len(focus_nodes)}, Context nodes: {len(context_nodes)}")


if __name__ == "__main__":
    main()