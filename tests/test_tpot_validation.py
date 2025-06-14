import importlib
import importlib.util
import os
import types
import sys
import pytest


def load_module(monkeypatch):
    stub_names = ['pandas', 'rich', 'rich.console', 'rich.tree', 'sklearn', 'sklearn.base', 'components.base']
    for name in stub_names:
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))

    sys.modules['rich.console'].Console = type('Console', (), {'__init__': lambda self, *a, **k: None})
    sys.modules['rich.tree'].Tree = type('Tree', (), {})
    sys.modules['sklearn.base'].BaseEstimator = object
    sys.modules['components.base'].BaseEngine = object

    spec = importlib.util.spec_from_file_location(
        'engines.tpot_wrapper',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'engines', 'tpot_wrapper.py'),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules['engines.tpot_wrapper'] = module
    sys.modules.setdefault('engines', types.ModuleType('engines')).tpot_wrapper = module
    spec.loader.exec_module(module)
    return module


def test_validate_tpot_parameters(monkeypatch):
    mod = load_module(monkeypatch)

    with pytest.raises(ValueError):
        mod._validate_tpot_parameters(["BadModel"], [], "r2")
    with pytest.raises(ValueError):
        mod._validate_tpot_parameters([], ["BadPreprocessor"], "r2")
    with pytest.raises(ValueError):
        mod._validate_tpot_parameters([], [], "not_a_metric")

    mod._validate_tpot_parameters(["Ridge"], ["StandardScaler"], "r2")


