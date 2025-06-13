import sys
import types
import pathlib
import pytest

# Insert project root into path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# Provide lightweight stubs for heavy optional dependencies so that the
# orchestrator module can be imported without installing them.
dummy = types.ModuleType("dummy")
for name in [
    "pandas",
    "numpy",
    "sklearn",
    "sklearn.pipeline",
    "sklearn.model_selection",
    "sklearn.metrics",
    "rich",
]:
    sys.modules.setdefault(name, dummy)
dummy.random = types.SimpleNamespace(seed=lambda *a, **k: None)

sk_pipeline = types.ModuleType("sklearn.pipeline")
sk_pipeline.Pipeline = object
sys.modules["sklearn.pipeline"] = sk_pipeline
sk_model_sel = types.ModuleType("sklearn.model_selection")
sk_model_sel.RepeatedKFold = object
sk_model_sel.cross_validate = lambda *a, **k: None
sys.modules["sklearn.model_selection"] = sk_model_sel
sk_metrics = types.ModuleType("sklearn.metrics")
sk_metrics.make_scorer = lambda *a, **k: None
sk_metrics.mean_absolute_error = lambda *a, **k: 0
sk_metrics.r2_score = lambda *a, **k: 0
sk_metrics.mean_squared_error = lambda *a, **k: 0
sys.modules["sklearn.metrics"] = sk_metrics
sklearn_mod = types.ModuleType("sklearn")
sklearn_mod.pipeline = sk_pipeline
sklearn_mod.model_selection = sk_model_sel
sklearn_mod.metrics = sk_metrics
sys.modules["sklearn"] = sklearn_mod

rich_console = types.ModuleType("rich.console")
class DummyConsole:
    def __init__(self, *a, **k):
        pass
    def log(self, *a, **k):
        pass
rich_console.Console = DummyConsole
sys.modules.setdefault("rich.console", rich_console)
rich_tree = types.ModuleType("rich.tree")
class DummyTree:
    def __init__(self, *a, **k):
        pass
rich_tree.Tree = DummyTree
sys.modules.setdefault("rich.tree", rich_tree)

scripts = types.ModuleType("scripts")
data_loader = types.ModuleType("scripts.data_loader")
data_loader.load_data = lambda *a, **k: (None, None)
scripts.data_loader = data_loader
sys.modules.setdefault("scripts", scripts)
sys.modules.setdefault("scripts.data_loader", data_loader)

engines = types.ModuleType("engines")
engines.discover_available = lambda: {}
sys.modules.setdefault("engines", engines)
for wrapper in [
    "engines.auto_sklearn_wrapper",
    "engines.tpot_wrapper",
    "engines.autogluon_wrapper",
]:
    mod = types.ModuleType(wrapper)
    mod.AutoSklearnEngine = object
    mod.TPOTEngine = object
    mod.AutoGluonEngine = object
    sys.modules.setdefault(wrapper, mod)

import orchestrator


def test_validate_components_success():
    orchestrator._validate_components_availability()


def test_validate_components_missing_model(monkeypatch):
    monkeypatch.setattr(orchestrator, "MODEL_FAMILIES", orchestrator.MODEL_FAMILIES + ["FakeModel"])
    with pytest.raises(FileNotFoundError):
        orchestrator._validate_components_availability()


def test_cli_exits_on_missing_components(monkeypatch):
    def raise_missing():
        raise FileNotFoundError("missing")
    monkeypatch.setattr(orchestrator, "_validate_components_availability", raise_missing)
    monkeypatch.setattr(sys, "argv", ["prog", "--data", "d.csv", "--target", "t.csv", "--autogluon"])
    with pytest.raises(SystemExit) as exc:
        orchestrator._cli()
    assert exc.value.code == 1
