import os
import sys
import types
import importlib.util
from pathlib import Path
from unittest import mock

import pytest


def load_orchestrator():
    project_root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("orchestrator", project_root / "orchestrator.py")
    module = importlib.util.module_from_spec(spec)
    dummy = types.ModuleType("dummy")

    rich_console = types.ModuleType("rich.console")
    class DummyConsole:
        def __init__(self, *args, **kwargs):
            pass
        def log(self, *args, **kwargs):
            pass
    rich_console.Console = DummyConsole
    rich_tree = types.ModuleType("rich.tree")
    rich_tree.Tree = object
    rich_mod = types.ModuleType("rich")
    rich_mod.console = rich_console
    rich_mod.tree = rich_tree

    engines_mod = types.ModuleType("engines")
    auto_sklearn_mod = types.ModuleType("engines.auto_sklearn_wrapper")
    auto_sklearn_mod.AutoSklearnEngine = object
    tpot_mod = types.ModuleType("engines.tpot_wrapper")
    tpot_mod.TPOTEngine = object
    ag_mod = types.ModuleType("engines.autogluon_wrapper")
    ag_mod.AutoGluonEngine = object
    engines_mod.auto_sklearn_wrapper = auto_sklearn_mod
    engines_mod.tpot_wrapper = tpot_mod
    engines_mod.autogluon_wrapper = ag_mod
    engines_mod.discover_available = lambda: {}

    numpy_mod = types.ModuleType("numpy")
    class DummyRandom:
        def seed(self, *_args, **_kwargs):
            pass
    numpy_mod.random = DummyRandom()

    sklearn_mod = types.ModuleType("sklearn")
    sklearn_pipeline = types.ModuleType("sklearn.pipeline")
    sklearn_pipeline.Pipeline = object
    sklearn_model_selection = types.ModuleType("sklearn.model_selection")
    sklearn_model_selection.RepeatedKFold = object
    sklearn_model_selection.cross_validate = lambda *a, **k: None
    sklearn_metrics = types.ModuleType("sklearn.metrics")
    sklearn_metrics.make_scorer = lambda *a, **k: None
    sklearn_metrics.mean_absolute_error = lambda *a, **k: None
    sklearn_metrics.r2_score = lambda *a, **k: None
    sklearn_metrics.mean_squared_error = lambda *a, **k: None

    data_loader_mod = types.ModuleType("scripts.data_loader")
    data_loader_mod.load_data = lambda *a, **k: None

    scripts_mod = types.ModuleType("scripts")
    scripts_mod.data_loader = data_loader_mod

    patches = {
        "pandas": dummy,
        "rich": rich_mod,
        "rich.console": rich_console,
        "rich.tree": rich_tree,
        "scripts": scripts_mod,
        "scripts.data_loader": data_loader_mod,
        "engines": engines_mod,
        "engines.auto_sklearn_wrapper": auto_sklearn_mod,
        "engines.tpot_wrapper": tpot_mod,
        "engines.autogluon_wrapper": ag_mod,
        "numpy": numpy_mod,
        "sklearn": sklearn_mod,
        "sklearn.pipeline": sklearn_pipeline,
        "sklearn.model_selection": sklearn_model_selection,
        "sklearn.metrics": sklearn_metrics,
        "logstash_async.handler": dummy,
        "logstash_async.formatter": dummy,
    }
    with mock.patch.dict(sys.modules, patches):
        spec.loader.exec_module(module)
    return module


orchestrator = load_orchestrator()


def test_validate_components_success():
    orchestrator._validate_components_availability()


def test_validate_components_missing_model(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "MODEL_FAMILIES",
        orchestrator.MODEL_FAMILIES + ["NonExistentModel"],
        raising=False,
    )
    with pytest.raises(RuntimeError):
        orchestrator._validate_components_availability()


def test_validate_components_missing_prep(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "PREP_STEPS",
        orchestrator.PREP_STEPS + ["NonExistentPrep"],
        raising=False,
    )
    with pytest.raises(RuntimeError):
        orchestrator._validate_components_availability()
