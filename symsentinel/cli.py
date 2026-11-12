"""Command-Line Interface (CLI) for SymSentinel.

Provides commands to:
  - verify-gates: Run the pre-registered Research Gates G0-G4.
  - simulate: Run real-time synthetic quantum hardware drift simulations.
  - search-corpus: Query the 100 indexed scientific research papers.
  - dashboard: Launch the interactive web visual laboratory in the browser.
  - bundle: Package the paper and figures into an Overleaf/arXiv submission bundle.
"""

import argparse
import json
import os
import subprocess
import sys
import webbrowser

from symsentinel import __version__


def cmd_verify_gates(args):
    """Run research gate verification script."""
    print("=" * 75)
    print(" SYMSENTINEL: RUNNING PRE-REGISTERED RESEARCH GATES G0 TO G4")
    print("=" * 75)
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "run_experiments.py")
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found.")
        sys.exit(1)
    subprocess.run([sys.executable, script_path], check=True)


def cmd_simulate(args):
    """Run standalone synthetic drift simulation."""
    from symsentinel.api import SymSentinel, SymSentinelConfig
    from symsentinel.sim.drift import DriftSimulator

    print(f"Running simulation: Regime={args.regime}, Epochs={args.epochs}, Shots={args.shots}")
    config = SymSentinelConfig(
        num_qubits=args.qubits,
        symmetry="z2",
        risk_target=args.tau,
        alpha=args.alpha,
    )
    engine = SymSentinel(config=config)
    sim = DriftSimulator(num_qubits=args.qubits, target_parity=0, seed=42)

    for ep in range(1, args.epochs + 1):
        if args.regime == "D1":
            bits, nu = sim.sample_d1_coherent(epoch=ep, num_shots=args.shots)
        elif args.regime == "D2":
            bits, nu = sim.sample_d2_incoherent(epoch=ep, num_shots=args.shots)
        else:
            bits, nu, _ = sim.sample_d3_jump(epoch=ep, jump_epoch=args.epochs // 2, num_shots=args.shots)

        report = engine.step(bits)
        if ep % 10 == 0 or report["action"] != "CONTINUE":
            print(f"Epoch {ep:2d} | Violation: {report['violation_rate']:.4f} | E-Detector: {report['edetector_stat']:8.2f} | Action: {report['action']:<20} | Cert: {report['certificate']:.4f}")


def cmd_search_corpus(args):
    """Search 100 indexed papers."""
    search_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "search_papers.py")
    if not os.path.exists(search_script):
        print(f"Error: {search_script} not found.")
        sys.exit(1)
    cmd = [sys.executable, search_script, args.query]
    if args.section:
        cmd.extend(["--section", str(args.section)])
    subprocess.run(cmd, check=True)


def cmd_dashboard(args):
    """Open interactive web laboratory in default browser."""
    dash_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "index.html")
    if not os.path.exists(dash_path):
        print(f"Error: {dash_path} not found.")
        sys.exit(1)
    print(f"Launching SymSentinel Interactive Dashboard: {dash_path}")
    webbrowser.open(f"file://{os.path.abspath(dash_path)}")


def cmd_bundle(args):
    """Bundle paper and figures into an Overleaf/arXiv zip archive."""
    import zipfile
    base_dir = os.path.dirname(os.path.dirname(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    zip_path = os.path.join(dist_dir, "SymSentinel_Submission_Bundle.zip")

    print(f"Packaging submission bundle to: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add paper files
        paper_dir = os.path.join(base_dir, "paper")
        for f in os.listdir(paper_dir):
            full_path = os.path.join(paper_dir, f)
            if os.path.isfile(full_path):
                zf.write(full_path, arcname=f"paper/{f}")

        # Add figures
        fig_dir = os.path.join(base_dir, "figures")
        if os.path.exists(fig_dir):
            for f in os.listdir(fig_dir):
                full_path = os.path.join(fig_dir, f)
                if os.path.isfile(full_path):
                    zf.write(full_path, arcname=f"figures/{f}")

    print(f"Successfully created submission bundle ({os.path.getsize(zip_path) / 1024:.1f} KB).")


def main():
    parser = argparse.ArgumentParser(
        prog="symsentinel",
        description="SymSentinel: Zero-Overhead Hardware Drift Sentinel for Quantum Machine Learning",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # verify-gates
    subparsers.add_parser("verify-gates", help="Run pre-registered Research Gates G0 to G4")

    # simulate
    sim_parser = subparsers.add_parser("simulate", help="Run synthetic hardware drift simulation")
    sim_parser.add_argument("--regime", choices=["D1", "D2", "D3"], default="D1", help="Drift regime")
    sim_parser.add_argument("--epochs", type=int, default=60, help="Number of operational epochs")
    sim_parser.add_argument("--shots", type=int, default=2048, help="Shots per epoch")
    sim_parser.add_argument("--qubits", type=int, default=6, help="Number of qubits")
    sim_parser.add_argument("--tau", type=float, default=0.08, help="Target risk tolerance")
    sim_parser.add_argument("--alpha", type=float, default=0.05, help="Significance level")

    # search-corpus
    search_parser = subparsers.add_parser("search-corpus", help="Search 100 indexed scientific research papers")
    search_parser.add_argument("query", help="Keyword or topic to search")
    search_parser.add_argument("--section", type=int, choices=range(1, 8), help="Filter by research pillar (1-7)")

    # dashboard
    subparsers.add_parser("dashboard", help="Open the interactive web laboratory in browser")

    # bundle
    subparsers.add_parser("bundle", help="Package paper, figures, and data into arXiv/Overleaf zip")

    args = parser.parse_args()
    if args.command == "verify-gates":
        cmd_verify_gates(args)
    elif args.command == "simulate":
        cmd_simulate(args)
    elif args.command == "search-corpus":
        cmd_search_corpus(args)
    elif args.command == "dashboard":
        cmd_dashboard(args)
    elif args.command == "bundle":
        cmd_bundle(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
