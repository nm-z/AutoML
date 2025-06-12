import pandas as pd
from orchestrator import _meta_search_sequential


def test_meta_search_sequential(tmp_path):
    X = pd.DataFrame({'a': range(20), 'b': range(20, 40)})
    y = pd.Series(range(20))
    champ, results, metrics = _meta_search_sequential(
        X, y, run_dir=tmp_path, timeout_per_engine=1, metric='r2'
    )
    assert champ is not None
    assert isinstance(results, dict)
    assert len(results) >= 1
    assert isinstance(metrics, dict)
    assert len(metrics) == len(results)
