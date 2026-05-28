"""
HN Audience Map - Static Visualization v5
- Baseten forced onto map (the key finding)
- Green edges showing audience movement
- Combined legend (size key + color code) in bottom-LEFT corner
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from pathlib import Path

DATA_DIR = Path("data")
OVERLAP_FILE = DATA_DIR / "overlap_matrix.json"
OUTPUT_FILE = "hn_audience_map.png"

FOCUS_DOMAINS = {
    "baseten.com", "modal.com", "replicate.com", "runpod.io",
    "together.ai", "anyscale.com", "huggingface.co", "fireworks.ai",
    "langchain.com", "llamaindex.ai", "wandb.ai", "pinecone.io",
    "weaviate.io", "trychroma.com", "mlflow.org", "bentoml.com", "ray.io",
}

MIN_OVERLAP_COEF = 0.10


def short_name(domain):
    for suffix in (".com", ".ai", ".io", ".org", ".co"):
        domain = domain.replace(suffix, "")
    return domain


def main():
    with open(OVERLAP_FILE) as f:
        data = json.load(f)

    G = nx.Graph()
    for node in data["nodes"]:
        G.add_node(node["domain"], size=node["commenter_count"])

    for edge in data["edges"]:
        if edge["overlap_coefficient"] >= MIN_OVERLAP_COEF:
            G.add_edge(edge["source"], edge["target"],
                       weight=edge["overlap_coefficient"])

    # Remove isolated nodes EXCEPT baseten
    isolates = [n for n in nx.isolates(G) if n != "baseten.com"]
    G.remove_nodes_from(isolates)

    if "baseten.com" not in G.nodes():
        G.add_node("baseten.com", size=1)

    # Layout for connected nodes only
    G_connected = G.copy()
    if "baseten.com" in G_connected.nodes() and G_connected.degree("baseten.com") == 0:
        G_connected.remove_node("baseten.com")
    pos = nx.spring_layout(G_connected, k=0.6, iterations=50, seed=42)

    # Manually place baseten
    pos["baseten.com"] = (0.05, 0.62)

    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_facecolor("#0d1117")
    fig.patch.set_facecolor("#0d1117")

    focus_nodes = [n for n in G.nodes() if n in FOCUS_DOMAINS and n != "baseten.com"]
    context_nodes = [n for n in G.nodes() if n not in FOCUS_DOMAINS]

    def node_size(n):
        return 80 + (G.nodes[n]["size"] ** 0.5) * 12

    # Context edges (faint gray)
    context_edges = [(u, v) for u, v in G.edges()
                     if u not in FOCUS_DOMAINS or v not in FOCUS_DOMAINS]
    nx.draw_networkx_edges(G, pos, edgelist=context_edges,
                           edge_color="#30363d", width=0.5, alpha=0.4, ax=ax)

    # Focus edges (bright green = audience movement)
    focus_edges = [(u, v) for u, v in G.edges()
                   if u in FOCUS_DOMAINS and v in FOCUS_DOMAINS]
    nx.draw_networkx_edges(G, pos, edgelist=focus_edges,
                           edge_color="#3fb950", width=2.0, alpha=0.9, ax=ax)

    # Context nodes (gray)
    nx.draw_networkx_nodes(G, pos, nodelist=context_nodes,
                           node_size=[node_size(n) for n in context_nodes],
                           node_color="#484f58", alpha=0.5, ax=ax)

    # Focus nodes (blue)
    nx.draw_networkx_nodes(G, pos, nodelist=focus_nodes,
                           node_size=[node_size(n) for n in focus_nodes],
                           node_color="#58a6ff", alpha=0.95, ax=ax)

    # Baseten (orange, ringed)
    nx.draw_networkx_nodes(G, pos, nodelist=["baseten.com"],
                           node_size=[600],
                           node_color="#f78166", alpha=1.0,
                           edgecolors="#ffffff", linewidths=2, ax=ax)

    # Labels
    context_labels = {n: short_name(n) for n in context_nodes}
    focus_labels = {n: short_name(n) for n in focus_nodes}
    nx.draw_networkx_labels(G, pos, labels=context_labels,
                            font_size=8, font_color="#8b949e", ax=ax)
    nx.draw_networkx_labels(G, pos, labels=focus_labels,
                            font_size=10, font_color="#ffffff",
                            font_weight="bold", ax=ax)
    nx.draw_networkx_labels(G, pos, labels={"baseten.com": "BASETEN"},
                            font_size=13, font_color="#f78166",
                            font_weight="bold", ax=ax)

    # Annotation callout pointing at Baseten
    bx, by = pos["baseten.com"]
    ax.annotate(
        "Baseten has effectively no\nHN audience - 0 shared\ncommenters with any peer.\nIts competitors (Modal,\nReplicate, Together) do.",
        xy=(bx, by), xytext=(bx - 0.65, by - 0.08),
        fontsize=10, color="#f78166",
        ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#161b22",
                  edgecolor="#f78166", alpha=0.95),
        arrowprops=dict(arrowstyle="->", color="#f78166", lw=1.5),
    )

    ax.set_title(
        "HN Audience Overlap Map - Where Baseten Operates in the AI Conversation",
        color="#ffffff", fontsize=16, pad=20,
    )

    # ---- Combined legend in bottom-LEFT (size key on top, color code below) ----
    circle_x = 0.04    # x position of reference circles (left side)
    label_x = 0.065    # x position of size labels (just right of circles)

    # Size key header
    size_top = 0.30
    size_step = 0.055
    ax.text(circle_x - 0.02, size_top + size_step,
            "Circle size = # of HN commenters",
            transform=ax.transAxes, color="#c9d1d9", fontsize=10,
            fontweight="bold", ha="left", va="center")

    size_refs = [(50, "~50 commenters"),
                 (950, "~950 commenters"),
                 (9000, "~9,000 commenters")]
    for i, (count, label) in enumerate(size_refs):
        y = size_top - i * size_step
        marker_size = 80 + (count ** 0.5) * 12
        ax.scatter([circle_x], [y], s=marker_size,
                   color="#8b949e", alpha=0.7,
                   transform=ax.transAxes, clip_on=False)
        ax.text(label_x, y, label,
                transform=ax.transAxes, color="#c9d1d9",
                fontsize=9, va="center", ha="left")

    # Color legend below the size key (bottom-left)
    legend_elements = [
        mpatches.Patch(color="#3fb950", label="Audience movement (infra cluster)"),
        mpatches.Patch(color="#58a6ff", label="AI infra companies (focus)"),
        mpatches.Patch(color="#484f58", label="Foundation models / hyperscalers (context)"),
        mpatches.Patch(color="#f78166", label="Baseten (no measurable HN audience)"),
    ]
    ax.legend(handles=legend_elements,
              loc="lower left",
              bbox_to_anchor=(0.0, 0.0),
              facecolor="#161b22", edgecolor="#30363d",
              labelcolor="#c9d1d9", fontsize=9)

    ax.axis("off")
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150, facecolor="#0d1117", bbox_inches="tight")
    print(f"Saved to {OUTPUT_FILE}")
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")


if __name__ == "__main__":
    main()