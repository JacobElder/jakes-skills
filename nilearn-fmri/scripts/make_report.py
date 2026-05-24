"""
Generate an HTML GLM report from an already-fitted first- or second-level model
that was pickled to disk.

Usage
-----
python make_report.py \
    --model model.pkl \
    --contrasts "face - house" "house" \
    --threshold 3.1 \
    --height-control fdr \
    --alpha 0.05 \
    --out report.html
"""

import argparse
import pickle


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", required=True, help="Pickled FirstLevelModel or SecondLevelModel")
    p.add_argument("--contrasts", nargs="+", required=True)
    p.add_argument("--threshold", type=float, default=3.1)
    p.add_argument("--cluster-threshold", type=int, default=10)
    p.add_argument("--height-control", default=None,
                   choices=[None, "fpr", "fdr", "bonferroni"],
                   help="None = use --threshold directly; else compute from --alpha")
    p.add_argument("--alpha", type=float, default=0.001)
    p.add_argument("--title", default="GLM Report")
    p.add_argument("--out", required=True, help="Output HTML path")
    args = p.parse_args()

    with open(args.model, "rb") as f:
        model = pickle.load(f)

    contrasts = {c: c for c in args.contrasts}

    report = model.generate_report(
        contrasts=contrasts,
        threshold=args.threshold,
        cluster_threshold=args.cluster_threshold,
        height_control=args.height_control,
        alpha=args.alpha,
        title=args.title,
    )
    report.save_as_html(args.out)
    print(f"Report saved to {args.out}")


if __name__ == "__main__":
    main()
