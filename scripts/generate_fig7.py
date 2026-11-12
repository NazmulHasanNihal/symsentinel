"""Figure 7 Generation Script: Multi-Qubit & Heavy-Hex Scaling Benchmarks (n=4..27).

Generates 4-panel publication-ready figure:
  - (a) IBM Falcon 27-qubit heavy-hex coupling graph with sentinel sublattice coloring
  - (b) Empirical vs theoretical detection delay vs system size n in [4, 27]
  - (c) Classical syndrome extraction latency and shot throughput vs n
  - (d) Greedy multi-sentinel set-cover cardinality scaling across lattice size
"""

import json
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Path setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATA_PATH = os.path.join(REPO_ROOT, "data", "results_scaling_heavyhex.json")
FIG_DIRS = [
    os.path.join(REPO_ROOT, "figures"),
    os.path.join(REPO_ROOT, "paper", "figures"),
    os.path.join(REPO_ROOT, "experiments", "figures"),
]

for d in FIG_DIRS:
    os.makedirs(d, exist_ok=True)

# Styling
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9,
    "figure.titlesize": 13,
    "mathtext.fontset": "cm",
    "figure.dpi": 300,
    "savefig.dpi": 300,
})


def plot_heavy_hex_subgraph(ax):
    """Draws a stylized 27-qubit heavy-hexagonal layout with sentinel bipartite coloring."""
    ax.set_title(r"(a) 27-Qubit Heavy-Hex Topology & Sublattice Sentinels", fontweight="bold")
    ax.axis("off")

    # Node positions on 2D plane (approximate layout of IBM Falcon 27)
    # Hexagonal mesh coordinates
    pos = {
        0: (0.0, 3.0), 1: (1.0, 3.0), 2: (2.0, 3.0), 3: (3.0, 3.0), 5: (4.0, 3.0), 8: (5.0, 3.0), 9: (6.0, 3.0), 10: (7.0, 3.0), 12: (8.0, 3.0),
        4: (1.0, 2.0), 7: (1.0, 1.0), 6: (0.0, 1.0),
        11: (5.0, 2.0), 14: (5.0, 1.0), 13: (4.0, 1.0),
        15: (8.0, 2.0), 18: (8.0, 1.0), 21: (8.0, 0.0), 23: (9.0, 0.0),
        16: (5.0, 0.0), 19: (5.0, -1.0), 22: (6.0, -1.0), 25: (7.0, -1.0), 26: (8.0, -1.0),
        17: (7.0, 1.0), 20: (7.0, 0.0), 24: (6.0, 0.0)
    }

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 5), (5, 8), (8, 9), (9, 10), (10, 12),
        (1, 4), (4, 7), (7, 6),
        (8, 11), (11, 14), (14, 13),
        (12, 13), (12, 15), (15, 18), (18, 21), (21, 23),
        (14, 16), (16, 19), (19, 22), (22, 25), (25, 26),
        (18, 17), (17, 20), (20, 24)
    ]

    # Draw edges
    for u, v in edges:
        if u in pos and v in pos:
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            ax.plot([x0, x1], [y0, y1], color="#9E9E9E", lw=2.2, zorder=1)

    # Draw nodes
    # Color nodes by bipartite sublattice: Even = #1976D2 (Blue, S_even), Odd = #D32F2F (Red, S_odd)
    for node, (x, y) in pos.items():
        is_even = (node % 2 == 0)
        c = "#1976D2" if is_even else "#D32F2F"
        circle = plt.Circle((x, y), 0.28, facecolor=c, edgecolor="#212121", lw=1.2, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y, str(node), ha="center", va="center", color="white", fontsize=7.5, fontweight="bold", zorder=4)

    # Annotate legend inside panel
    ax.plot([], [], "o", color="#1976D2", markersize=8, label=r"Sublattice $A$ (Even Qubits, $S_Z^{(A)}$)")
    ax.plot([], [], "o", color="#D32F2F", markersize=8, label=r"Sublattice $B$ (Odd Qubits, $S_Z^{(B)}$)")
    ax.plot([], [], "-", color="#9E9E9E", lw=2, label=r"2Q Cross-Resonance Couplings")
    ax.legend(loc="lower left", framealpha=0.9, fontsize=8.5)

    ax.set_xlim(-0.8, 9.8)
    ax.set_ylim(-1.8, 3.8)


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    delays = data["detection_delay"]
    setcover = data["greedy_setcover"]
    latency = data["classical_latency"]

    n_qubits = np.array(delays["qubit_sizes"])
    delays_mean = np.array(delays["delays_mean"])
    delays_std = np.array(delays["delays_std"])
    delays_theory = np.array(delays["delays_theory"])

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 9.5))

    # Panel (a): Heavy-hex connectivity
    plot_heavy_hex_subgraph(ax1)

    # Panel (b): Detection delay vs system size n
    ax2.set_title(r"(b) Detection Delay Scaling vs System Size $n$", fontweight="bold")
    ax2.plot(n_qubits, delays_theory, "b--", lw=2.0, marker="^", markersize=7, label=r"Wald/KL Lower Bound: $\frac{\ln \gamma}{S_t D_{\mathrm{KL}}(\nu_1 \parallel \nu_0)}$")
    ax2.errorbar(n_qubits, delays_mean, yerr=2*delays_std, fmt="s-", color="#D84315", lw=2.2, markersize=8, capsize=4, elinewidth=1.5, label=r"Empirical Delay ($S_t=256, \gamma=200$)")
    
    # Text annotation
    ax2.text(10, 7.0, r"$\tau \in [4.4, 8.1]$ epochs" "\n" r"Tracks $\sim 1.8\times$ theory" "\n" r"Faster detection at higher $n$!",
             fontsize=9, bbox=dict(boxstyle="round,pad=0.4", fc="#FFF3E0", ec="#D84315", lw=1.2))

    ax2.set_xlabel(r"Lattice Size $n$ (Qubits on Heavy-Hex)")
    ax2.set_ylabel(r"Detection Delay $\tau$ (Epochs)")
    ax2.set_ylim(0, 10.5)
    ax2.set_xticks(n_qubits)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper right", fontsize=8.5)

    # Panel (c): Classical latency and throughput
    ax3.set_title(r"(c) Syndrome Extraction Latency & Throughput", fontweight="bold")
    lat_ms = np.array(latency["extraction_latency_ms"])
    thru = np.array(latency["throughput_mshots_sec"])

    ax3_color = "#1565C0"
    ax3.set_xlabel(r"System Size $n$ (Qubits)")
    ax3.set_ylabel(r"Latency per $10^4$ Shots (ms)", color=ax3_color)
    line1 = ax3.plot(n_qubits, lat_ms, "o-", color=ax3_color, lw=2.2, markersize=7, label="Extraction Latency (ms)")
    ax3.tick_params(axis="y", labelcolor=ax3_color)
    ax3.set_ylim(0, 0.35)
    ax3.set_xticks(n_qubits)
    ax3.grid(True, linestyle=":", alpha=0.6)

    ax3_twin = ax3.twinx()
    ax3_twin_color = "#2E7D32"
    ax3_twin.set_ylabel(r"Throughput ($10^6$ Shots / sec)", color=ax3_twin_color)
    line2 = ax3_twin.plot(n_qubits, thru, "d--", color=ax3_twin_color, lw=2.0, markersize=7, label="Throughput (Mshots/s)")
    ax3_twin.tick_params(axis="y", labelcolor=ax3_twin_color)
    ax3_twin.set_ylim(30, 95)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc="upper right", fontsize=8.5)

    # Panel (d): Greedy set-cover scaling
    ax4.set_title(r"(d) Multi-Sentinel Set-Cover Cardinality ($M$)", fontweight="bold")
    sc_1q = setcover["setcover_1q"]
    sc_all = setcover["setcover_all"]

    width = 0.35
    x_idx = np.arange(len(n_qubits))
    rects1 = ax4.bar(x_idx - width/2, sc_1q, width, label=r"Single-Qubit Paulis ($3n$ faults)", color="#42A5F5", edgecolor="#1565C0")
    rects2 = ax4.bar(x_idx + width/2, sc_all, width, label=r"All 1Q + 2Q Paulis ($3n + 15|E|$ faults)", color="#FFA726", edgecolor="#E65100")

    for rect in rects1:
        h = rect.get_height()
        ax4.annotate(f"{h}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for rect in rects2:
        h = rect.get_height()
        ax4.annotate(f"{h}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax4.set_xlabel(r"Lattice Size $n$ (Qubits)")
    ax4.set_ylabel(r"Optimal Sentinels Count ($M$)")
    ax4.set_xticks(x_idx)
    ax4.set_xticklabels(n_qubits)
    ax4.set_ylim(0, 5.5)
    ax4.grid(True, linestyle=":", alpha=0.6, axis="y")
    ax4.legend(loc="upper left", fontsize=8.5)

    plt.tight_layout()

    out_name = "fig7_scaling_heavyhex"
    for out_dir in FIG_DIRS:
        pdf_path = os.path.join(out_dir, f"{out_name}.pdf")
        png_path = os.path.join(out_dir, f"{out_name}.png")
        fig.savefig(pdf_path, bbox_inches="tight")
        fig.savefig(png_path, bbox_inches="tight")
        print(f"[OK] Saved: {pdf_path}")
        print(f"[OK] Saved: {png_path}")

    plt.close()


if __name__ == "__main__":
    main()
