# AB-Engine: A Statistical Experimentation Framework

AB-Engine is a product analytics case study that evaluates a controlled A/B experiment end to end: from deterministic assignment and metric comparison to guardrail evaluation and final rollout decision. The experiment shows a statistically significant lift in conversion, but the final recommendation is HOLD because bounce rate worsened enough to require investigation before shipping.

## Executive Summary

This experiment compared a control landing page against a treatment variant using a balanced sample of 20,000 users. The treatment produced a statistically significant increase in conversion, but the predefined guardrail metric for bounce rate deteriorated enough to block rollout.

The central takeaway is simple: a positive primary metric is not sufficient on its own when a user-experience guardrail moves in the wrong direction.

## Business Impact

- Identified a 6.92% statistically significant improvement in conversion.
- Prevented a potentially harmful rollout by detecting a statistically significant increase in bounce rate through guardrail monitoring.
- Demonstrated a decision framework that balances business growth with user experience rather than optimizing a single KPI.

## Business Context

Product teams often need to decide whether an experiment is ready to ship based on more than one metric. A treatment can improve conversion while still creating friction in the user journey, and that tradeoff matters when the goal is sustainable product growth.

This project models that decision process in a way that is reproducible, audit-friendly, and easy to explain to stakeholders.

## Problem Statement

The core question is not whether the treatment improves conversion in isolation. The real question is whether the treatment improves the business outcome enough to justify the risk of harming user experience.

In this experiment, the treatment increased conversion, but bounce rate also increased. The framework therefore needed to evaluate both the upside and the downside before making a rollout recommendation.

## Hypothesis

The hypothesis was that the treatment variant would improve conversion relative to control without creating unacceptable degradation in guardrail metrics.

The experiment was designed to test whether the conversion lift was strong enough to support rollout, while also checking whether user-experience or business-quality metrics remained within acceptable bounds.

## Experiment Design

The experiment used deterministic, stateless user assignment so the same user always maps to the same variant across reruns. That makes the experiment reproducible and avoids bucket instability.

The sample was split evenly across variants:
- Control: 9,996 users.
- Treatment: 10,004 users.

The analysis compared primary performance on conversion and then evaluated guardrail metrics before reaching a final recommendation.

## Dataset

The experiment dataset contains simulated user-level observations for the landing page test.

### Key dataset facts
- Sample balance: A = 9,996, B = 10,004.
- Primary metric: conversion.
- Guardrail metrics: bounce rate, revenue per visitor, and sample balance.
- Output dataset: `data/simulated/landing_page_v2_experiment.csv`.

The dataset is structured to support straightforward statistical analysis and decision memo generation.

## Methodology

The workflow follows a standard experimentation lifecycle:
1. Assign users deterministically to control or treatment.
2. Simulate experiment outcomes.
3. Compare the primary conversion metric.
4. Evaluate guardrail metrics.
5. Generate a final decision memo.

The emphasis is on decision quality, not just statistical significance. The experiment is considered successful only if the primary metric improves and the guardrails remain acceptable.

```mermaid
flowchart TD
    A[User Assignment] --> B[Control / Treatment Split]
    B --> C[Metric Collection]
    C --> D[Primary Metric Analysis]
    C --> E[Guardrail Evaluation]
    D --> F[Decision Framework]
    E --> F
    F --> G[Business Recommendation]
```

## Statistical Testing

The primary metric used a two-sample proportion test to compare conversion rates between control and treatment. The result showed a statistically significant improvement in conversion.

The guardrail analysis separately evaluated bounce rate, revenue per visitor, and sample balance. The key decision point was not whether the treatment won on conversion, but whether the guardrails remained stable enough to support rollout.

## Primary Metric

### Conversion
- Control conversion: 14.86%.
- Treatment conversion: 15.88%.
- Relative lift: 6.92%.
- p-value: 0.04391.

The treatment delivered a statistically significant improvement in conversion, which is a positive signal for the product.

## Guardrail Metrics

### Bounce Rate
- Control bounce rate: 32.22%.
- Treatment bounce rate: 33.78%.
- p-value: 0.01948.

Bounce rate worsened enough to trigger a guardrail HOLD. This is a user-experience risk and should be investigated before any rollout decision.

### Revenue per Visitor
- Control: $12.24.
- Treatment: $12.70.

Revenue per visitor improved, which supports the treatment from a business-value perspective, but it does not override the bounce-rate concern.

### Sample Balance
- A: 9,996.
- B: 10,004.

The sample split is well balanced, which supports the validity of the comparison.

## Results

The experiment produced a mixed but informative result:
- Conversion improved significantly.
- Revenue per visitor improved.
- Bounce rate worsened significantly.

The analysis therefore supports a HOLD decision rather than an immediate ship recommendation. The treatment shows upside, but the guardrail deterioration means the experiment is not ready for rollout without further investigation.

## Business Recommendation

**HOLD: Guardrail risk needs investigation.**

The statistically significant conversion lift is not enough to ship when a predefined user-experience guardrail worsens. The correct product decision is to pause rollout, review the bounce-rate regression, and determine whether the treatment’s conversion gain is worth the added friction.

```mermaid
flowchart TD
    A[Conversion Lift Observed] --> B{Guardrail Stable?}
    B -- Yes --> C[Ship]
    B -- No --> D[Hold]
    D --> E[Investigate Bounce Rate]
    E --> F[Reassess Rollout]
```

## Visual Story

The experiment summary is captured in a single visual report:

![Experiment Results](data/simulated/experiment_results_chart.png)

This figure brings together the conversion comparison, treatment-effect confidence interval, and guardrail summary in one place. It is the fastest way to understand why the result is not a straightforward ship decision.

## Production Considerations

This project is designed as a reproducible experimentation workflow, not as a deployed product system. The focus is on clear decision logic, deterministic assignment, transparent metrics, and auditable outputs.

Supporting artifacts, including a detailed implementation report (`REPORT.md`) and an automatically generated stakeholder decision memo (`data/simulated/decision_memo.md`), are included for reproducibility and auditability.

## Project Architecture

```mermaid
flowchart LR
    A[Config] --> B[Deterministic Assignment]
    B --> C[Simulation / Metric Generation]
    C --> D[Statistical Testing]
    D --> E[Guardrail Evaluation]
    E --> F[Decision Memo]
    F --> G[Visual Report]
```

## Repository Structure

```text
ab_engine/
├── README.md
├── REPORT.md
├── config/
│   └── experiment_config.yaml
├── data/
│   └── simulated/
│       ├── experiment_results_chart.png
│       ├── decision_memo.md
│       └── landing_page_v2_experiment.csv
├── main.py
├── notebooks/
│   └── 01_experiment_walkthrough.ipynb
├── requirements.txt
└── src/
    └── engine/
        ├── randomization.py
        ├── simulator.py
        └── stats.py
```

## Key Learnings

- Statistical significance alone is not enough to justify a rollout.
- Guardrail metrics are essential for balancing growth and user experience.
- Deterministic assignment makes experimentation reproducible and easier to audit.
- A concise decision memo is often more valuable than a long technical explanation when communicating results.

## How to Run

```bash
python main.py
```

The project also includes a notebook walkthrough and generated output files in `data/simulated/` for review.

## Technologies Used

- Python
- NumPy
- pandas
- SciPy
- Matplotlib
- YAML
- Jupyter Notebook
- Mermeid.js
