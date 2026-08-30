# Documentation for `training/fair_eval.py`


## Functions

### Function `_binom_two_sided_exact_p`

Two-sided exact test for Binomial(n, p); used for McNemar discordant pairs (p=0.5).

### Function `mcnemar_discordant`

McNemar on paired binary outcomes.
b01 = count(baseline True, oracle False); b10 = count(baseline False, oracle True).

### Function `paired_mcnemar_analysis`

Paired McNemar for headline binaries (same rows as Wilson chart).

### Function `wilson_interval`

Wilson score interval for a binomial proportion.
Returns (low, high, p_hat). For n==0 returns (nan, nan, nan).

### Function `_binary_keys`

No documentation provided.

### Function `analyze_per_episode`

No documentation provided.

### Function `_paired_improvement_counts`

Operational 'wins' where oracle strictly improves a binary bad outcome vs baseline.

### Function `plot_fair_eval`

Bar chart: select headline baseline vs oracle binary rates with Wilson error bars.

### Function `main`

No documentation provided.

### Function `pmf`

No documentation provided.

### Function `pair`

No documentation provided.

### Function `rate`

No documentation provided.

### Function `errs`

No documentation provided.
