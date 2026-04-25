from __future__ import annotations

from training.fair_eval import mcnemar_discordant, paired_mcnemar_analysis


def test_mcnemar_no_discordant_is_neutral() -> None:
    r = mcnemar_discordant(0, 0)
    assert r["n_discordant"] == 0
    assert r["p_value_two_sided_exact"] == 1.0


def test_mcnemar_strong_asymmetry_low_p() -> None:
    r = mcnemar_discordant(9, 1)
    assert r["n_discordant"] == 10
    assert r["p_value_two_sided_exact"] < 0.05


def test_paired_mcnemar_analysis_shape() -> None:
    rows = [
        {
            "binary": {
                "baseline_any_peak_violation": True,
                "oracle_any_peak_violation": False,
                "baseline_any_anti_cheat": False,
                "oracle_any_anti_cheat": False,
                "baseline_any_critical_defer": False,
                "oracle_any_critical_defer": False,
                "baseline_high_stress": False,
                "oracle_high_stress": False,
            }
        }
    ]
    out = paired_mcnemar_analysis(rows)
    assert "any_peak_violation" in out
    assert out["any_peak_violation"]["b01_baseline_pos_oracle_neg"] == 1
    assert out["any_peak_violation"]["b10_baseline_neg_oracle_pos"] == 0
