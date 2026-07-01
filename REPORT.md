# Landing Page V2 Experiment Report

## Decision

HOLD: Guardrail risk needs investigation.

## Key Result

Treatment conversion is higher than control and statistically significant:

- Control: 14.86%
- Treatment: 15.88%
- Relative lift: 6.92%
- p-value: 0.04391
- 95% CI for absolute conversion change: 0.03% to 2.03%

The primary metric improved, but this is not an automatic ship decision because the guardrail readout shows user-experience risk.

## Guardrails

- Bounce rate: risk. Treatment bounce increased from 32.22% to 33.78%.
- Revenue per visitor: clear. Treatment revenue per visitor increased from $12.24 to $12.70.
- Sample size balance: clear. A=9,996 and B=10,004.

## Business Recommendation

Do not ship Landing Page V2 to all traffic yet. The conversion lift is promising, but the higher bounce rate suggests the redesign may be creating friction for some users. This is a HOLD decision because a statistically significant primary metric does not outweigh a meaningful guardrail risk. Investigate the drop-off pattern, adjust the page, and rerun or continue the test before a full rollout.

Generated outputs:

- `data/simulated/landing_page_v2_experiment.csv`
- `data/simulated/experiment_results_chart.png`
- `data/simulated/decision_memo.md`

The chart summarizes the variant conversion rates, confidence interval for the treatment effect, and guardrail movement in one stakeholder-friendly visual.
