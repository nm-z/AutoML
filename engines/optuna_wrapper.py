from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from rich.console import Console
from rich.tree import Tree
from sklearn.base import BaseEstimator

from components.base import BaseEngine
from scripts.config import DEFAULT_METRIC

console = Console(highlight=False)
logger = logging.getLogger(__name__)


class OptunaEngine(BaseEngine):
    """Optuna adapter conforming to the orchestrator's API."""

    def __init__(self, seed: int, timeout_sec: int, run_dir: Path):
        self.seed = seed
        self.timeout_sec = timeout_sec
        self.run_dir = run_dir
        self._study: Any = None
        self._best_model: BaseEstimator | None = None
        self._metric: str = DEFAULT_METRIC

    @property
    def name(self) -> str:
        return "OptunaEngine"

    @property
    def best_pipeline_info(self) -> dict:
        if self._best_model is None:
            return {"status": "not_fitted"}
        if self._study is not None:
            return {
                "score": self._study.best_value,
                "params": self._study.best_params,
                "metric": self._metric,
                "pipeline_description": "Ridge optimized by Optuna",
            }
        return {"status": "fitted", "details": "Fallback model"}

    @property
    def run_info(self) -> dict:
        if self._best_model is None:
            return {"status": "not_fitted"}
        return {
            "best_score": self.best_pipeline_info.get("score", "N/A"),
            "run_dir": str(self.run_dir),
            "log": str(self.run_dir.parent / "logs" / f"{self.name}.log"),
            "artefact_paths": {
                "model_pickle": str(self.run_dir / "model.pkl"),
                "optuna_trials_csv": str(self.run_dir / "optuna_trials.csv"),
            },
        }

    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> BaseEstimator:
        root = Tree("[Optuna]")
        logger.info("[%s] search-start", self.__class__.__name__)

        self._metric = kwargs.get("metric", DEFAULT_METRIC)

        try:
            import optuna
            from sklearn.linear_model import Ridge
            from sklearn.model_selection import cross_val_score

            root.add("library detected – running real Optuna")

            def objective(trial: optuna.trial.Trial) -> float:
                alpha = trial.suggest_float("alpha", 1e-3, 10.0, log=True)
                model = Ridge(alpha=alpha)
                scores = cross_val_score(
                    model,
                    X,
                    y,
                    cv=3,
                    scoring=self._metric,
                    n_jobs=1,
                )
                return scores.mean()

            direction = "maximize" if self._metric == "r2" else "minimize"
            self._study = optuna.create_study(direction=direction)
            self._study.optimize(objective, timeout=self.timeout_sec)

            best_alpha = self._study.best_params.get("alpha", 1.0)
            self._best_model = Ridge(alpha=best_alpha)
            self._best_model.fit(X, y)
            logger.info(
                "[%s] best-score: %s", self.__class__.__name__, self._study.best_value
            )
        except ModuleNotFoundError as e:
            logger.warning(
                "[%s] library missing – fallback LinearRegression: %s",
                self.__class__.__name__,
                e,
            )
            from sklearn.linear_model import LinearRegression

            linreg = LinearRegression(n_jobs=1)
            linreg.fit(X, y)
            self._best_model = linreg
        console.print(root)
        logger.info("[%s] search-end", self.__class__.__name__)
        return self._best_model

    def predict(self, X: pd.DataFrame) -> pd.Series:
        if self._best_model is None:
            raise RuntimeError("Model not fitted. Call fit() first.")
        return self._best_model.predict(X)

    def export(self, path: Path):
        if self._best_model is None:
            raise RuntimeError("Model not fitted. Call fit() first.")
        import joblib

        path.mkdir(parents=True, exist_ok=True)
        model_file = path / "model.pkl"
        joblib.dump(self._best_model, model_file)
        logger.info("[%s] Saved champion model to %s", self.__class__.__name__, model_file)

        if self._study is not None:
            trials_df = self._study.trials_dataframe()
            trials_df.to_csv(path / "optuna_trials.csv", index=False)
            logger.info(
                "[%s] Saved Optuna trials to %s",
                self.__class__.__name__,
                path / "optuna_trials.csv",
            )


__all__ = ["OptunaEngine"]
