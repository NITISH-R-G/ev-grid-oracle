# Documentation for training/fair_eval.py

## Functions

### _binom_two_sided_exact_p
```text
Two-sided exact test for Binomial(n, p); used for McNemar discordant pairs (p=0.5).
```

### mcnemar_discordant
```text
McNemar on paired binary outcomes.
b01 = count(baseline True, oracle False); b10 = count(baseline False, oracle True).
```

### paired_mcnemar_analysis
```text
Paired McNemar for headline binaries (same rows as Wilson chart).
```

### wilson_interval
```text
Wilson score interval for a binomial proportion.
Returns (low, high, p_hat). For n==0 returns (nan, nan, nan).
```

### _binary_keys
### analyze_per_episode
### _paired_improvement_counts
```text
Operational 'wins' where oracle strictly improves a binary bad outcome vs baseline.
```

### plot_fair_eval
```text
Bar chart: select headline baseline vs oracle binary rates with Wilson error bars.
```

### main
### pmf
### pair
### rate
### errs
