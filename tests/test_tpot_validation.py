import importlib.util
from pathlib import Path
import sys
import types
import pytest


def load_tpot_wrapper(monkeypatch):
    module_name = 'engines.tpot_wrapper'
    sys.modules.pop(module_name, None)

    pandas = types.ModuleType('pandas')
    monkeypatch.setitem(sys.modules, 'pandas', pandas)

    sklearn = types.ModuleType('sklearn')
    base_mod = types.ModuleType('sklearn.base')
    base_mod.BaseEstimator = object
    sklearn.base = base_mod
    monkeypatch.setitem(sys.modules, 'sklearn', sklearn)
    monkeypatch.setitem(sys.modules, 'sklearn.base', base_mod)

    rich_console = types.ModuleType('rich.console')
    class DummyConsole:
        def __init__(self, *a, **k):
            pass
        def print(self, *a, **k):
            pass
    rich_console.Console = DummyConsole
    monkeypatch.setitem(sys.modules, 'rich.console', rich_console)
    rich_tree = types.ModuleType('rich.tree')
    rich_tree.Tree = type('Tree', (), {})
    monkeypatch.setitem(sys.modules, 'rich.tree', rich_tree)

    components = types.ModuleType('components')
    base_engine_mod = types.ModuleType('components.base')
    base_engine_mod.BaseEngine = object
    components.base = base_engine_mod
    monkeypatch.setitem(sys.modules, 'components', components)
    monkeypatch.setitem(sys.modules, 'components.base', base_engine_mod)

    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).resolve().parents[1] / 'engines' / 'tpot_wrapper.py',
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validate_parameters_success(monkeypatch):
    mod = load_tpot_wrapper(monkeypatch)
    mod._validate_parameters('r2', ['Ridge'], ['StandardScaler'])


def test_validate_parameters_invalid_metric(monkeypatch):
    mod = load_tpot_wrapper(monkeypatch)
    with pytest.raises(ValueError):
        mod._validate_parameters('bad', ['Ridge'], ['StandardScaler'])


def test_validate_parameters_invalid_model(monkeypatch):
    mod = load_tpot_wrapper(monkeypatch)
    with pytest.raises(ValueError):
        mod._validate_parameters('r2', ['UnknownModel'], ['StandardScaler'])


def test_validate_parameters_invalid_preprocessor(monkeypatch):
    mod = load_tpot_wrapper(monkeypatch)
    with pytest.raises(ValueError):
        mod._validate_parameters('r2', ['Ridge'], ['FakeScaler'])
