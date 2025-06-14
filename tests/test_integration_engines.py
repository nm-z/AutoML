import importlib.util
from pathlib import Path
import sys
import types

import pytest
fit_calls = {"autosklearn": False, "tpot": False, "autogluon": False}


def load_orchestrator(monkeypatch):
    sys.modules.pop("orchestrator", None)

    pandas = types.ModuleType("pandas")
    monkeypatch.setitem(sys.modules, "pandas", pandas)

    numpy = types.ModuleType("numpy")
    numpy.random = types.SimpleNamespace(seed=lambda *a, **k: None)
    numpy.sqrt = lambda x: x ** 0.5
    numpy.array = lambda x: x
    numpy.mean = lambda x: 0
    numpy.std = lambda x: 0
    numpy.inf = float("inf")
    monkeypatch.setitem(sys.modules, "numpy", numpy)

    rich_console = types.ModuleType("rich.console")
    class DummyConsole:
        def __init__(self, *a, **k):
            pass
        def log(self, *a, **k):
            pass
        def print(self, *a, **k):
            pass
    rich_console.Console = DummyConsole
    monkeypatch.setitem(sys.modules, "rich.console", rich_console)

    rich_tree = types.ModuleType("rich.tree")
    class DummyTree:
        def __init__(self, *a, **k):
            pass
        def add(self, *a, **k):
            return DummyTree()
    rich_tree.Tree = DummyTree
    monkeypatch.setitem(sys.modules, "rich.tree", rich_tree)

    sklearn = types.ModuleType("sklearn")
    monkeypatch.setitem(sys.modules, "sklearn", sklearn)
    pipe_mod = types.ModuleType("sklearn.pipeline")
    pipe_mod.Pipeline = object
    monkeypatch.setitem(sys.modules, "sklearn.pipeline", pipe_mod)
    msel = types.ModuleType("sklearn.model_selection")
    class DummyRKF:
        def __init__(self, *a, **k):
            pass
    msel.RepeatedKFold = DummyRKF
    msel.cross_validate = lambda *a, **k: {
        "test_r2": [0],
        "test_rmse": [0],
        "test_mae": [0],
    }
    def train_test_split(X, y, *a, **k):
        return X, X, y, y
    msel.train_test_split = train_test_split
    monkeypatch.setitem(sys.modules, "sklearn.model_selection", msel)

    metrics = types.ModuleType("sklearn.metrics")
    metrics.make_scorer = lambda *a, **k: None
    metrics.mean_absolute_error = lambda *a, **k: 0
    metrics.mean_squared_error = lambda *a, **k: 0
    metrics.r2_score = lambda *a, **k: 0
    monkeypatch.setitem(sys.modules, "sklearn.metrics", metrics)

    data_loader = types.ModuleType("scripts.data_loader")
    class DummyX(list):
        shape = (1, 1)
    class DummyY(list):
        shape = (1,)
    def load_data(*a, **k):
        return DummyX([0]), DummyY([1])
    data_loader.load_data = load_data
    monkeypatch.setitem(sys.modules, "scripts.data_loader", data_loader)

    engines_mod = types.ModuleType("engines")
    monkeypatch.setitem(sys.modules, "engines", engines_mod)
    for key, wrapper, cls_name in [
        ("autosklearn", "auto_sklearn_wrapper", "AutoSklearnEngine"),
        ("tpot", "tpot_wrapper", "TPOTEngine"),
        ("autogluon", "autogluon_wrapper", "AutoGluonEngine"),
    ]:
        mod = types.ModuleType(f"engines.{wrapper}")
        def make_engine(name):
            class DummyEngine:
                def __init__(self, *a, **k):
                    pass
                def fit(self, X, y):
                    fit_calls[name] = True
                    class Model:
                        def predict(self, X):
                            return [0]
                    return Model()
            return DummyEngine
        mod.__all__ = [cls_name]
        mod.__dict__[cls_name] = make_engine(key)
        monkeypatch.setitem(sys.modules, f"engines.{wrapper}", mod)
    def discover_available():
        return {
            "autosklearn": sys.modules["engines.auto_sklearn_wrapper"],
            "tpot": sys.modules["engines.tpot_wrapper"],
            "autogluon": sys.modules["engines.autogluon_wrapper"],
        }
    engines_mod.discover_available = discover_available

    import pickle as real_pickle
    pickle_stub = types.ModuleType("pickle")
    pickle_stub.__dict__.update(vars(real_pickle))
    pickle_stub.dump = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, "pickle", pickle_stub)

    spec = importlib.util.spec_from_file_location(
        "orchestrator",
        Path(__file__).resolve().parents[1] / "orchestrator.py",
    )
    orch = importlib.util.module_from_spec(spec)
    sys.modules["orchestrator"] = orch
    spec.loader.exec_module(orch)
    return orch


def test_all_engines_run(monkeypatch, tmp_path):
    orch = load_orchestrator(monkeypatch)

    monkeypatch.setattr(orch, "_validate_components_availability", lambda: None)
    monkeypatch.setattr(orch, "_extract_pipeline_info", lambda m: {})

    def fake_meta_search(**kwargs):
        run_dir = Path(kwargs.get("run_dir"))
        run_dir.mkdir(parents=True, exist_ok=True)
        for k in fit_calls:
            fit_calls[k] = True
        class DummyModel:
            def predict(self, X):
                return [0]
        dummy = DummyModel()
        return dummy, {k: dummy for k in fit_calls}, {k: {} for k in fit_calls}

    monkeypatch.setattr(orch, "_meta_search_concurrent", fake_meta_search)
    monkeypatch.setattr(orch, "_meta_search_sequential", fake_meta_search)

    data = tmp_path / "p.csv"
    target = tmp_path / "t.csv"
    data.write_text("a\n1\n")
    target.write_text("b\n1\n")

    monkeypatch.setattr(sys, "argv", [
        "orchestrator.py",
        "--data",
        str(data),
        "--target",
        str(target),
        "--all",
        "--no-ensemble",
    ])

    orch._cli()

    assert all(fit_calls.values())


