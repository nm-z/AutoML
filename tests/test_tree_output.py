import importlib
import importlib.util
import os
import sys
import types
from pathlib import Path


def load_orchestrator(monkeypatch, console_cls, tree_cls):
    stub_names = [
        'pandas',
        'numpy',
        'sklearn',
        'sklearn.pipeline',
        'sklearn.model_selection',
        'sklearn.metrics',
        'rich',
        'rich.console',
        'rich.tree',
        'scripts',
        'scripts.data_loader',
        'engines',
        'engines.auto_sklearn_wrapper',
        'engines.tpot_wrapper',
        'engines.autogluon_wrapper',
    ]
    for name in stub_names:
        module = types.ModuleType(name)
        monkeypatch.setitem(sys.modules, name, module)

    sys.modules['numpy'].random = types.SimpleNamespace(seed=lambda *a, **k: None)

    console_mod = types.ModuleType('rich.console')
    console_mod.Console = console_cls
    monkeypatch.setitem(sys.modules, 'rich.console', console_mod)

    tree_mod = types.ModuleType('rich.tree')
    tree_mod.Tree = tree_cls
    monkeypatch.setitem(sys.modules, 'rich.tree', tree_mod)

    dl_mod = sys.modules['scripts.data_loader']
    dl_mod.load_data = lambda *a, **k: (None, None)
    sys.modules['engines'].discover_available = lambda: {}
    sys.modules['engines.auto_sklearn_wrapper'].AutoSklearnEngine = object
    sys.modules['engines.tpot_wrapper'].TPOTEngine = object
    sys.modules['engines.autogluon_wrapper'].AutoGluonEngine = object
    pipe_mod = types.ModuleType('sklearn.pipeline')
    pipe_mod.Pipeline = object
    monkeypatch.setitem(sys.modules, 'sklearn.pipeline', pipe_mod)
    msel = types.ModuleType('sklearn.model_selection')
    msel.RepeatedKFold = object
    msel.cross_validate = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, 'sklearn.model_selection', msel)
    metrics = types.ModuleType('sklearn.metrics')
    metrics.make_scorer = lambda *a, **k: None
    metrics.mean_absolute_error = lambda *a, **k: None
    metrics.mean_squared_error = lambda *a, **k: None
    metrics.r2_score = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, 'sklearn.metrics', metrics)

    spec = importlib.util.spec_from_file_location(
        'orchestrator',
        Path(__file__).resolve().parents[1] / 'orchestrator.py',
    )
    orchestrator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(orchestrator)
    return orchestrator


class CaptureTree:
    def __init__(self, label):
        self.label = label
        self.children = []

    def add(self, label):
        child = CaptureTree(label)
        self.children.append(child)
        return child


class CaptureConsole:
    def __init__(self, *a, **k):
        self.captured = None

    def log(self, *a, **k):
        pass

    def print(self, obj):
        self.captured = obj


def test_print_artifact_tree(tmp_path, monkeypatch):
    sub = tmp_path / 'subdir'
    sub.mkdir()
    (sub / 'file.txt').write_text('x')

    console = CaptureConsole()
    orch = load_orchestrator(monkeypatch, lambda *a, **k: console, CaptureTree)

    orch._print_artifact_tree(tmp_path)

    tree = console.captured
    assert any('subdir' in child.label for child in tree.children)
    sub_child = next(c for c in tree.children if 'subdir' in c.label)
    assert any('file.txt' in c.label for c in sub_child.children)

