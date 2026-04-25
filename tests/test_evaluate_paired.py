from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _chdir_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(REPO_ROOT)


def test_baseline_rollout_identical_for_same_seed_and_scenario() -> None:
    from training.evaluate import run_episode

    env = EVGridCore(city_graph=build_city_graph())
    a = run_episode(env, policy="baseline", seed=42, scenario="baseline")
    b = run_episode(env, policy="baseline", seed=42, scenario="baseline")
    assert a == b


def test_oracle_matches_baseline_when_skip_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORACLE_SKIP_LLM", "1")
    from training.evaluate import run_episode

    env = EVGridCore(city_graph=build_city_graph())
    base = run_episode(env, policy="baseline", seed=7, scenario="heatwave_peak")
    ora = run_episode(env, policy="oracle", seed=7, scenario="heatwave_peak")
    assert base == ora


def test_evaluate_cli_paired_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORACLE_SKIP_LLM", "1")
    out = tmp_path / "eval_results.json"
    subprocess.check_call(
        [
            sys.executable,
            str(REPO_ROOT / "training" / "evaluate.py"),
            "--episodes",
            "2",
            "--seed",
            "100",
            "--scenario",
            "baseline",
            "--out",
            str(out),
        ],
        cwd=str(REPO_ROOT),
        env={**os.environ, "ORACLE_SKIP_LLM": "1"},
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data.get("paired_same_world") is True
    assert len(data["per_episode"]) == 2
    row0 = data["per_episode"][0]
    assert row0["episode_seed"] == 100
    assert row0["baseline"] == row0["oracle"]


def test_fair_eval_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORACLE_SKIP_LLM", "1")
    ev_json = tmp_path / "eval_results.json"
    subprocess.check_call(
        [
            sys.executable,
            str(REPO_ROOT / "training" / "evaluate.py"),
            "--episodes",
            "3",
            "--seed",
            "1",
            "--out",
            str(ev_json),
        ],
        cwd=str(REPO_ROOT),
        env={**os.environ, "ORACLE_SKIP_LLM": "1"},
    )
    fair_json = tmp_path / "fair_eval_results.json"
    fair_png = tmp_path / "fair_eval_chart.png"
    subprocess.check_call(
        [
            sys.executable,
            str(REPO_ROOT / "training" / "fair_eval.py"),
            "--eval-json",
            str(ev_json),
            "--out-json",
            str(fair_json),
            "--out-chart",
            str(fair_png),
        ],
        cwd=str(REPO_ROOT),
    )
    fe = json.loads(fair_json.read_text(encoding="utf-8"))
    assert fe["n_episodes"] == 3
    assert "binary_rates_wilson" in fe
    assert "baseline_any_peak_violation" in fe["binary_rates_wilson"]
    assert "paired_mcnemar" in fe
    assert "any_peak_violation" in fe["paired_mcnemar"]
    assert fair_png.is_file()
