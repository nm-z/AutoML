import pandas as pd
import pytest

from engines.auto_sklearn_wrapper import AutoSklearnEngine
from engines.tpot_wrapper import TPOTEngine
from engines.autogluon_wrapper import AutoGluonEngine


def _sample_data():
    X = pd.DataFrame({'a': range(10), 'b': range(10, 20)})
    y = pd.Series(range(10))
    return X, y


def test_auto_sklearn_engine(tmp_path):
    pytest.importorskip('autosklearn')
    X, y = _sample_data()
    engine = AutoSklearnEngine(seed=0, timeout_sec=10, run_dir=tmp_path)
    engine.fit(X, y)
    preds = engine.predict(X)
    assert len(preds) == len(y)
    engine.export(tmp_path)


def test_tpot_engine(tmp_path):
    X, y = _sample_data()
    engine = TPOTEngine(seed=0, timeout_sec=1, run_dir=tmp_path)
    engine.fit(X, y)
    preds = engine.predict(X)
    assert len(preds) == len(y)


def test_autogluon_engine(tmp_path):
    X, y = _sample_data()
    engine = AutoGluonEngine(seed=0, timeout_sec=1, run_dir=tmp_path)
    engine.fit(X, y)
    preds = engine.predict(X)
    assert len(preds) == len(y)
    try:
        engine.export(tmp_path)
    except Exception:
        pass
