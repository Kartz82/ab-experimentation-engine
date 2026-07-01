import numpy as np
from statistics import NormalDist
from typing import Dict, List, Union


NORMAL = NormalDist()

class ExperimentStats:
    @staticmethod
    def calculate_sample_size(baseline: float, mde: float, alpha: float = 0.05, power: float = 0.8) -> int:
        """Calculates required sample size per variant for a 2-sample proportion test."""
        p1 = baseline
        p2 = baseline * (1 + mde)
        p_avg = (p1 + p2) / 2
        
        z_alpha = NORMAL.inv_cdf(1 - alpha / 2)
        z_beta = NORMAL.inv_cdf(power)
        
        n = (z_alpha * np.sqrt(2 * p_avg * (1 - p_avg)) + z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2 / (p1 - p2)**2
        return int(np.ceil(n))

    @staticmethod
    def analyze_proportions(count_a: int, nob_a: int, count_b: int, nob_b: int, alpha: float = 0.05) -> Dict[str, Union[float, bool, list]]:
        """Performs a two-sample Z-test for proportions."""
        p_a = count_a / nob_a
        p_b = count_b / nob_b
        p_pooled = (count_a + count_b) / (nob_a + nob_b)
        
        se = np.sqrt(p_pooled * (1 - p_pooled) * (1/nob_a + 1/nob_b))
        z_stat = (p_b - p_a) / se
        p_value = 2 * (1 - NORMAL.cdf(abs(z_stat)))
        
        ci_lower = (p_b - p_a) - NORMAL.inv_cdf(1 - alpha / 2) * se
        ci_upper = (p_b - p_a) + NORMAL.inv_cdf(1 - alpha / 2) * se
        
        return {
            "p_a": round(p_a, 4),
            "p_b": round(p_b, 4),
            "lift": round((p_b - p_a) / p_a, 4),
            "p_value": round(p_value, 5),
            "ci": [round(ci_lower, 4), round(ci_upper, 4)],
            "significant": bool(p_value < alpha)
        }

    @staticmethod
    def analyze_binary_metric(df, metric: str, alpha: float = 0.05) -> Dict[str, Union[str, float, bool, list]]:
        """Analyzes a binary metric split by variants A and B."""
        counts = df.groupby("variant")[metric].agg(["sum", "count"])
        result = ExperimentStats.analyze_proportions(
            count_a=counts.loc["A", "sum"],
            nob_a=counts.loc["A", "count"],
            count_b=counts.loc["B", "sum"],
            nob_b=counts.loc["B", "count"],
            alpha=alpha,
        )
        result["metric"] = metric
        return result

    @staticmethod
    def analyze_mean_metric(df, metric: str, alpha: float = 0.05) -> Dict[str, Union[str, float, bool, list]]:
        """Analyzes a continuous metric with a Welch t-test and normal CI."""
        a = df.loc[df["variant"] == "A", metric]
        b = df.loc[df["variant"] == "B", metric]

        mean_a = a.mean()
        mean_b = b.mean()
        lift = (mean_b - mean_a) / mean_a if mean_a else 0
        se = np.sqrt(b.var(ddof=1) / len(b) + a.var(ddof=1) / len(a))
        delta = mean_b - mean_a
        z_stat = delta / se if se else 0
        p_value = 2 * (1 - NORMAL.cdf(abs(z_stat)))
        ci_delta = NORMAL.inv_cdf(1 - alpha / 2) * se

        return {
            "metric": metric,
            "mean_a": round(mean_a, 4),
            "mean_b": round(mean_b, 4),
            "lift": round(lift, 4),
            "p_value": round(float(p_value), 5),
            "ci": [round(delta - ci_delta, 4), round(delta + ci_delta, 4)],
            "significant": bool(p_value < alpha),
        }

    @staticmethod
    def analyze_sample_balance(df, tolerance: float = 0.02) -> Dict[str, Union[str, float, bool]]:
        """Checks whether variant assignment is close enough to a 50/50 split."""
        counts = df["variant"].value_counts()
        n_a = int(counts.get("A", 0))
        n_b = int(counts.get("B", 0))
        total = n_a + n_b
        share_b = n_b / total if total else 0
        imbalance = abs(share_b - 0.5)

        return {
            "metric": "sample_size_balance",
            "n_a": n_a,
            "n_b": n_b,
            "share_b": round(share_b, 4),
            "imbalance": round(imbalance, 4),
            "threshold": tolerance,
            "violated": bool(imbalance > tolerance),
        }

    @staticmethod
    def get_decision(primary_result: Dict, guardrail_results: List[Dict]) -> str:
        """Determines if a feature should be shipped based on primary results and guardrails."""
        # 1. Check Primary Metric
        is_positive = primary_result.get('significant', False) and primary_result.get('lift', 0) > 0
        
        # 2. Check Guardrails (Block if any significant drop > 2%)
        guardrail_violated = any(
            g.get("violated", False) or (g.get('significant', False) and g.get('lift', 0) < -0.02)
            for g in guardrail_results
        )
        
        if guardrail_violated:
            return "HOLD: Guardrail risk needs investigation"
        if is_positive:
            return "SHIP: Statistically significant conversion gain with acceptable guardrails"
        
        return "INVESTIGATE: Keep control live and collect more evidence"

    @staticmethod
    def visualize_results(results: Dict, output_path: str = "experiment_plot.png", guardrails: List[Dict] = None):
        """Generates and saves a compact chart for the primary metric and guardrails."""
        import os
        from pathlib import Path

        os.environ.setdefault("MPLCONFIGDIR", "data/simulated/.matplotlib")
        os.environ.setdefault("XDG_CACHE_HOME", "data/simulated/.cache")
        Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
        Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)
        import matplotlib.pyplot as plt

        guardrails = guardrails or []
        
        labels = ['Control (A)', 'Treatment (B)']
        rates = [results['p_a'] * 100, results['p_b'] * 100]

        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

        bars = axes[0].bar(labels, rates, color=['#6b7280', '#2563eb'])
        axes[0].set_ylabel('Conversion Rate (%)')
        axes[0].set_title('Primary Metric')
        for bar in bars:
            yval = bar.get_height()
            axes[0].text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{yval:.2f}%", ha='center', va='bottom', fontweight='bold')

        delta = (results["p_b"] - results["p_a"]) * 100
        ci = [value * 100 for value in results["ci"]]
        axes[1].axvline(0, color="#111827", linewidth=1)
        axes[1].errorbar(
            delta,
            0,
            xerr=[[delta - ci[0]], [ci[1] - delta]],
            fmt="o",
            color="#2563eb",
            capsize=5,
        )
        axes[1].set_yticks([])
        axes[1].set_xlabel("Absolute conversion change (percentage points)")
        axes[1].set_title("Treatment Effect and CI")
        axes[1].grid(axis="x", alpha=0.25)

        guardrail_labels = []
        guardrail_lifts = []
        guardrail_colors = []
        for guardrail in guardrails:
            if "lift" in guardrail:
                guardrail_labels.append(guardrail.get("name", guardrail["metric"]).replace("_", " ").title())
                guardrail_lifts.append(guardrail["lift"] * 100)
                guardrail_colors.append("#dc2626" if guardrail.get("violated") else "#16a34a")

        if guardrail_labels:
            axes[2].barh(guardrail_labels, guardrail_lifts, color=guardrail_colors)
            axes[2].axvline(0, color="#111827", linewidth=1)
            axes[2].set_xlabel("Treatment lift vs control (%)")
        else:
            axes[2].text(0.5, 0.5, "No guardrails", ha="center", va="center")
            axes[2].set_axis_off()
        axes[2].set_title("Guardrail Summary")
            
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        print(f"Chart saved to {output_path}")
        plt.close()
