import pandas as pd
import pytest
from pathlib import Path
import sys
from pathlib import Path as _Path

sys.path.append(str(_Path(__file__).resolve().parents[1]))

from scripts.data_loader import load_data


def test_load_csv(tmp_path):
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    target = pd.Series([0, 1], name='target')
    csv_x = tmp_path / 'X.csv'
    csv_y = tmp_path / 'y.csv'
    df.to_csv(csv_x, index=False)
    target.to_csv(csv_y, index=False, header=True)

    X, y = load_data(csv_x, csv_y)
    pd.testing.assert_frame_equal(X, df)
    pd.testing.assert_series_equal(y, target)


def test_load_parquet(tmp_path):
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    target = pd.Series([0, 1], name='target')
    pq_x = tmp_path / 'X.parquet'
    pq_y = tmp_path / 'y.parquet'
    df.to_parquet(pq_x)
    target.to_frame().to_parquet(pq_y)

    X, y = load_data(pq_x, pq_y)
    pd.testing.assert_frame_equal(X, df)
    pd.testing.assert_series_equal(y, target)


def test_missing_parquet_engine(monkeypatch, tmp_path):
    df = pd.DataFrame({'a': [1]})
    pq_x = tmp_path / 'x.parquet'
    pq_y = tmp_path / 'y.parquet'
    df.to_parquet(pq_x)
    df.to_parquet(pq_y)

    monkeypatch.setattr('importlib.util.find_spec', lambda name: None)
    with pytest.raises(ImportError):
        load_data(pq_x, pq_y)

