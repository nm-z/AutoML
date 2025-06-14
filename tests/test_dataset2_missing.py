import importlib
import importlib.util
import sys
import types
from pathlib import Path

import pytest


def load_orchestrator(monkeypatch, printed):
    sys.modules.pop("orchestrator", None)

    pandas = types.ModuleType("pandas")
    monkeypatch.setitem(sys.modules, "pandas", pandas)

    numpy = types.ModuleType("numpy")
    numpy.random = types.SimpleNamespace(seed=lambda *a, **k: None)
    numpy.sqrt = lambda x: x ** 0.5
    numpy.array = lambda x: x
    monkeypatch.setitem(sys.modules, "numpy", numpy)

    rich_console = types.ModuleType("rich.console")
    class DummyConsole:
        def __init__(self, *a, **k):
            pass
        def log(self, *a, **k):
            printed.append(a[0] if a else "")
        def print(self, obj):
            printed.append(obj)
    rich_console.Console = DummyConsole
    monkeypatch.setitem(sys.modules, "rich.console", rich_console)

    rich_tree = types.ModuleType("rich.tree")
    rich_tree.Tree = type("Tree", (), {})
    monkeypatch.setitem(sys.modules, "rich.tree", rich_tree)

    sklearn = types.ModuleType("sklearn")
    monkeypatch.setitem(sys.modules, "sklearn", sklearn)
    pipe_mod = types.ModuleType("sklearn.pipeline")
    pipe_mod.Pipeline = object
    monkeypatch.setitem(sys.modules, "sklearn.pipeline", pipe_mod)
    msel = types.ModuleType("sklearn.model_selection")
    msel.RepeatedKFold = object
    msel.cross_validate = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, "sklearn.model_selection", msel)
    metrics = types.ModuleType("sklearn.metrics")
    metrics.make_scorer = lambda *a, **k: None
    metrics.mean_absolute_error = lambda *a, **k: 0
    metrics.mean_squared_error = lambda *a, **k: 0
    metrics.r2_score = lambda *a, **k: 0
    monkeypatch.setitem(sys.modules, "sklearn.metrics", metrics)

    data_loader = types.ModuleType("scripts.data_loader")
    data_loader.load_data = lambda *a, **k: (None, None)
    monkeypatch.setitem(sys.modules, "scripts.data_loader", data_loader)

    engines_mod = types.ModuleType("engines")
    monkeypatch.setitem(sys.modules, "engines", engines_mod)
    for wrapper, cls_name in [
        ("auto_sklearn_wrapper", "AutoSklearnEngine"),
        ("tpot_wrapper", "TPOTEngine"),
        ("autogluon_wrapper", "AutoGluonEngine"),
    ]:
        mod = types.ModuleType(f"engines.{wrapper}")
        mod.__all__ = [cls_name]
        mod.__dict__[cls_name] = type(cls_name, (), {})
        monkeypatch.setitem(sys.modules, f"engines.{wrapper}", mod)
    engines_mod.discover_available = lambda: {
        "autosklearn": sys.modules["engines.auto_sklearn_wrapper"],
        "tpot": sys.modules["engines.tpot_wrapper"],
        "autogluon": sys.modules["engines.autogluon_wrapper"],
    }

    spec = importlib.util.spec_from_file_location(
        "orchestrator",
        Path(__file__).resolve().parents[1] / "orchestrator.py",
    )
    orch = importlib.util.module_from_spec(spec)
    sys.modules["orchestrator"] = orch
    spec.loader.exec_module(orch)
    return orch


def test_dataset2_missing_files(monkeypatch, tmp_path):
    printed = []
    orch = load_orchestrator(monkeypatch, printed)
    monkeypatch.setattr(orch, "_validate_components_availability", lambda: None)

    data = tmp_path / "DataSets" / "2" / "D2-Predictors.csv"
    target = tmp_path / "DataSets" / "2" / "D2-Targets.csv"
    monkeypatch.setattr(sys, "argv", [
        "orchestrator.py",
        "--data", str(data),
        "--target", str(target),
        "--all",
    ])
    with pytest.raises(SystemExit):
        orch._cli()
    assert any("Dataset 2 files are missing" in str(item) for item in printed)
