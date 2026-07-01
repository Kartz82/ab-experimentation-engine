from pathlib import Path

import pandas as pd
import yaml

from src.engine.simulator import ExperimentSimulator
from src.engine.stats import ExperimentStats


OUTPUT_DIR = Path("data/simulated")
DATASET_PATH = OUTPUT_DIR / "landing_page_v2_experiment.csv"
CHART_PATH = OUTPUT_DIR / "experiment_results_chart.png"
MEMO_PATH = OUTPUT_DIR / "decision_memo.md"


def format_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def build_guardrails(df: pd.DataFrame, alpha: float) -> list[dict]:
    bounce = ExperimentStats.analyze_binary_metric(df, "bounced", alpha=alpha)
    bounce["name"] = "Bounce rate"
    bounce["direction"] = "lower_is_better"
    bounce["violated"] = bool(bounce["significant"] and bounce["lift"] > 0.02)

    revenue = ExperimentStats.analyze_mean_metric(df, "revenue", alpha=alpha)
    revenue["name"] = "Revenue per visitor"
    revenue["direction"] = "higher_is_better"
    revenue["violated"] = bool(revenue["significant"] and revenue["lift"] < -0.02)

    balance = ExperimentStats.analyze_sample_balance(df)
    balance["name"] = "Sample size balance"

    return [bounce, revenue, balance]


def summarize_guardrail_risk(guardrails: list[dict]) -> str:
    violated = [g["name"] for g in guardrails if g.get("violated")]
    if not violated:
        return "No blocking guardrail risk detected."
    return "Blocking guardrail risk: " + ", ".join(violated) + "."


def write_decision_memo(primary: dict, guardrails: list[dict], decision: str) -> None:
    guardrail_lines = []
    for guardrail in guardrails:
        if guardrail["metric"] == "sample_size_balance":
            guardrail_lines.append(
                f"- {guardrail['name']}: A={guardrail['n_a']:,}, B={guardrail['n_b']:,}, "
                f"B share={format_pct(guardrail['share_b'])}, threshold={format_pct(guardrail['threshold'])}, "
                f"status={'risk' if guardrail['violated'] else 'clear'}"
            )
        elif "p_a" in guardrail:
            guardrail_lines.append(
                f"- {guardrail['name']}: A={format_pct(guardrail['p_a'])}, "
                f"B={format_pct(guardrail['p_b'])}, lift={format_pct(guardrail['lift'])}, "
                f"p={guardrail['p_value']}, status={'risk' if guardrail['violated'] else 'clear'}"
            )
        else:
            guardrail_lines.append(
                f"- {guardrail['name']}: A=${guardrail['mean_a']:.2f}, "
                f"B=${guardrail['mean_b']:.2f}, lift={format_pct(guardrail['lift'])}, "
                f"p={guardrail['p_value']}, status={'risk' if guardrail['violated'] else 'clear'}"
            )

    memo = f"""# Landing Page V2 Decision Memo

## Primary Metric Result

- Primary metric: conversion rate
- Control conversion: {format_pct(primary['p_a'])}
- Treatment conversion: {format_pct(primary['p_b'])}
- Relative lift: {format_pct(primary['lift'])}
- p-value: {primary['p_value']}
- 95% CI for absolute conversion change: {format_pct(primary['ci'][0])} to {format_pct(primary['ci'][1])}
- Statistically significant: {primary['significant']}

The treatment improved the primary metric, but the decision should account for guardrails before recommending a rollout.

## Guardrail Results

{chr(10).join(guardrail_lines)}

## Final Recommendation

{decision}

Business interpretation: {summarize_guardrail_risk(guardrails)} A statistically significant lift is not enough to ship if a customer-experience guardrail worsens.

## Next Action

Do not roll out Landing Page V2 to all traffic yet. Investigate the bounce-rate increase, review where users are dropping off, and rerun or continue the experiment after the page issue is addressed.
"""
    MEMO_PATH.write_text(memo)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open("config/experiment_config.yaml", "r") as file:
        config = yaml.safe_load(file)

    experiment_id = config["experiment_name"]
    params = config["parameters"]
    baseline = params["baseline_value"]
    mde = params["mde"]
    alpha = params["alpha"]
    n_users = params.get("n_users", 20000)
    seed = params.get("seed", 42)

    true_treatment_rate = baseline * (1 + mde)
    required_n = ExperimentStats.calculate_sample_size(baseline, mde, alpha, params["power"])

    print(f"Running case study: {experiment_id}")
    print(f"Business question: should Landing Page V2 ship to all traffic?")
    print(f"Required sample size per variant for target MDE: {required_n:,}")

    df = ExperimentSimulator.generate_data(
        n_users=n_users,
        exp_id=experiment_id,
        true_p_a=baseline,
        true_p_b=true_treatment_rate,
        seed=seed,
    )
    df.to_csv(DATASET_PATH, index=False)

    primary = ExperimentStats.analyze_binary_metric(df, "converted", alpha=alpha)
    guardrails = build_guardrails(df, alpha)
    decision = ExperimentStats.get_decision(primary, guardrails)

    print("\nExperiment Results")
    print("=" * 64)
    print(f"Control conversion:   {format_pct(primary['p_a'])}")
    print(f"Treatment conversion: {format_pct(primary['p_b'])}")
    print(f"Relative lift:        {format_pct(primary['lift'])}")
    print(f"P-value:              {primary['p_value']}")
    print(f"95% CI:               {format_pct(primary['ci'][0])} to {format_pct(primary['ci'][1])}")
    print(f"Decision:             {decision}")
    print("\nGuardrails")
    print("-" * 64)
    for guardrail in guardrails:
        status = "RISK" if guardrail.get("violated") else "clear"
        print(f"{guardrail['name']}: {status}")

    write_decision_memo(primary, guardrails, decision)
    ExperimentStats.visualize_results(primary, str(CHART_PATH), guardrails=guardrails)

    print("\nArtifacts")
    print("-" * 64)
    print(f"Dataset:       {DATASET_PATH}")
    print(f"Chart:         {CHART_PATH}")
    print(f"Decision memo: {MEMO_PATH}")


if __name__ == "__main__":
    main()
