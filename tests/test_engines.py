import builtins
from pathlib import Path
import sys

# Ensure repository root is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pytest
from sklearn.datasets import make_regression

from engines.autogluon_wrapper import AutoGluonEngine
from engines.auto_sklearn_wrapper import AutoSklearnEngine
from engines.tpot_wrapper import TPOTEngine


@pytest.fixture
def data():
    X, y = make_regression(n_samples=20, n_features=5, random_state=0)
    X = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])
    y = pd.Series(y)
    return X, y


def _force_missing(monkeypatch, prefix: str):
    original_import = builtins.__import__

    def mocked_import(name, *args, **kwargs):
        if name.startswith(prefix):
            raise ModuleNotFoundError(f"No module named {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mocked_import)


def _run_engine(engine_cls, monkeypatch, tmp_path: Path, data, missing_prefix: str):
    _force_missing(monkeypatch, missing_prefix)
    engine = engine_cls(seed=0, timeout_sec=1, run_dir=tmp_path)
    if engine_cls.__name__ == "AutoSklearnEngine":
        monkeypatch.setattr(engine, "_translate_metric", lambda m: "r2")
    X, y = data
    engine.fit(X, y)
    preds = engine.predict(X)
    assert len(preds) == len(y)
    assert engine.name.endswith("Engine")


def test_autogluon_engine(monkeypatch, tmp_path, data):
    _run_engine(AutoGluonEngine, monkeypatch, tmp_path, data, "autogluon")


def test_autosklearn_engine(monkeypatch, tmp_path, data):
    _run_engine(AutoSklearnEngine, monkeypatch, tmp_path, data, "autosklearn")


def test_tpot_engine(monkeypatch, tmp_path, data):
    _run_engine(TPOTEngine, monkeypatch, tmp_path, data, "tpot")
