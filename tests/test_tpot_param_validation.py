import importlib
import sys
import types
import pytest


def load_wrapper(monkeypatch):
    sys.modules.pop('engines.tpot_wrapper', None)
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    monkeypatch.setitem(sys.modules, 'pandas', types.ModuleType('pandas'))
    rich_console = types.ModuleType('rich.console')
    rich_console.Console = type('Console', (), {'__init__': lambda self, *a, **k: None})
    monkeypatch.setitem(sys.modules, 'rich.console', rich_console)
    rich_tree = types.ModuleType('rich.tree')
    rich_tree.Tree = type('Tree', (), {})
    monkeypatch.setitem(sys.modules, 'rich.tree', rich_tree)
    sklearn_base = types.ModuleType('sklearn.base')
    sklearn_base.BaseEstimator = object
    monkeypatch.setitem(sys.modules, 'sklearn.base', sklearn_base)
    mod = importlib.import_module('engines.tpot_wrapper')
    importlib.reload(mod)
    return mod


def test_build_frozen_config_valid(monkeypatch):
    mod = load_wrapper(monkeypatch)
    cfg = mod._build_frozen_config(['Ridge'], ['PCA'])
    assert isinstance(cfg, dict)


def test_build_frozen_config_invalid_model(monkeypatch):
    mod = load_wrapper(monkeypatch)
    with pytest.raises(ValueError):
        mod._build_frozen_config(['BadModel'], ['PCA'])


def test_build_frozen_config_invalid_preprocessor(monkeypatch):
    mod = load_wrapper(monkeypatch)
    with pytest.raises(ValueError):
        mod._build_frozen_config(['Ridge'], ['BadPrep'])


def test_translate_metric(monkeypatch):
    mod = load_wrapper(monkeypatch)
    assert mod._translate_metric('neg_mean_squared_error') == 'neg_mean_squared_error'
    assert mod._translate_metric('unknown') == 'r2'
