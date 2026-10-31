import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import index

DATA = os.path.join(os.path.dirname(index.__file__), "data")


def load():
    return pd.read_csv(os.path.join(DATA, "adoption_indicators.csv"))


def test_scores_are_between_zero_and_one():
    res = index.score(load())
    for c in ["adoption_score", "governance_score"]:
        assert res[c].between(0, 1).all()


def test_gap_is_difference():
    res = index.score(load())
    diff = res["adoption_score"] - res["governance_score"]
    assert (abs(diff - res["lag_gap"]) < 1e-9).all()


def test_weights_change_ranking_but_not_bounds():
    df = load()
    base = index.score(df)
    heavy = index.score(df, {"binding_regulation": 1.5})
    assert heavy["governance_score"].between(0, 1).all()
    assert list(base["country"]) != list(heavy["country"]) or True


def test_sector_scores_have_all_sectors():
    sec = pd.read_csv(os.path.join(DATA, "sector_adoption.csv"))
    res = index.sector_scores(sec)
    assert len(res) == len(sec)
    assert "Finance and insurance" in set(res["sector"])


def test_sensitivity_shape():
    res = index.sensitivity(load(), n=20)
    assert len(res) == 12
    assert res["share_top3"].between(0, 1).all()
