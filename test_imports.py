import sys
print(f"Python version: {sys.version}")
try:
    import autogluon.tabular as ag
    print(f"\u2713 AutoGluon: {ag.__version__}")
except ImportError as e:
    print(f"\u2717 AutoGluon: {e}")
try:
    import tpot
    print(f"\u2713 TPOT: {tpot.__version__}")
except ImportError as e:
    print(f"\u2717 TPOT: {e}")
try:
    import autosklearn.regression
    import autosklearn
    print(f"\u2713 Auto-Sklearn: {autosklearn.__version__}")
except ImportError as e:
    print(f"\u2717 Auto-Sklearn: {e}")
