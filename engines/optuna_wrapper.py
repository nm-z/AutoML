"""Optuna engine wrapper."""
from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Any, Sequence

import pandas as pd
from rich.console import Console
from rich.tree import Tree
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold, cross_val_score

from components.base import BaseEngine
from scripts.config import DEFAULT_METRIC, get_space

# Estimator imports
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
)
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

# Preprocessor imports
from components.preprocessors.dimensionality.PCA import PCABlock
from components.preprocessors.scalers.RobustScaler import RobustScalerBlock
from components.preprocessors.scalers.StandardScaler import StandardScalerBlock
from components.preprocessors.scalers.QuantileTransform import QuantileTransformBlock
from components.preprocessors.outliers.IsolationForest import IsolationForestBlock
from components.preprocessors.outliers.LocalOutlierFactor import LOFBlock
from components.preprocessors.outliers.KMeansOutlier import KMeansOutlierBlock

console = Console(highlight=False)
logger = logging.getLogger(__name__)

MODEL_CLASS_MAP = {
    "Ridge": Ridge,
    "Lasso": Lasso,
    "ElasticNet": ElasticNet,
    "SVR": SVR,
    "DecisionTree": DecisionTreeRegressor,
    "RandomForest": RandomForestRegressor,
    "ExtraTrees": ExtraTreesRegressor,
    "GradientBoosting": GradientBoostingRegressor,
    "AdaBoost": AdaBoostRegressor,
    "MLP": MLPRegressor,
    "XGBoost": XGBRegressor,
    "LightGBM": LGBMRegressor,
}

PREPROCESSOR_CLASS_MAP = {
    "PCA": PCABlock,
    "RobustScaler": RobustScalerBlock,
    "StandardScaler": StandardScalerBlock,
    "QuantileTransform": QuantileTransformBlock,
    "KMeansOutlier": KMeansOutlierBlock,
    "IsolationForest": IsolationForestBlock,
    "LocalOutlierFactor": LOFBlock,
}


class OptunaEngine(BaseEngine):
    """Optuna-based AutoML engine."""

    def __init__(self, seed: int, timeout_sec: int, run_dir: Path):
        self.seed = seed
        self.timeout_sec = timeout_sec
        self.run_dir = run_dir
        self.best_pipeline: Pipeline | None = None
        self.best_score: float | None = None

    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> BaseEstimator:
        root = Tree("[Optuna]")
        logger.info("[%s] search-start", self.__class__.__name__)

        model_space = get_space("model")
        preproc_space = get_space("preprocessor")

        model_families: Sequence[str] = kwargs.get("model_families", model_space.keys())
        prep_steps: Sequence[str] = kwargs.get("prep_steps", preproc_space.keys())
        metric: str = kwargs.get("metric", DEFAULT_METRIC)

        try:
            import optuna

            def objective(trial: optuna.trial.Trial) -> float:
                fam = trial.suggest_categorical("model_family", [m for m in model_families if m in model_space])
                model_params = {
                    p: trial.suggest_categorical(f"{fam}_{p}", vals)
                    for p, vals in model_space[fam].items()
                }

                preproc_options = [None] + [p for p in prep_steps if p in preproc_space]
                prep = trial.suggest_categorical("preprocessor", preproc_options)
                prep_params: dict[str, Any] = {}
                if prep:
                    prep_params = {
                        p: trial.suggest_categorical(f"{prep}_{p}", vals)
                        for p, vals in preproc_space[prep].items()
                    }

                steps: list[tuple[str, Any]] = []
                if prep:
                    prep_cls = PREPROCESSOR_CLASS_MAP.get(prep)
                    if prep_cls:
                        steps.append(("preprocessor", prep_cls(**prep_params)))
                model_cls = MODEL_CLASS_MAP[fam]
                steps.append(("model", model_cls(**model_params)))
                pipe = Pipeline(steps)

                cv = KFold(n_splits=3, shuffle=True, random_state=self.seed)
                score = cross_val_score(pipe, X, y, cv=cv, scoring=metric, n_jobs=1).mean()
                return score

            study = optuna.create_study(
                direction="maximize",
                sampler=optuna.samplers.TPESampler(seed=self.seed),
            )
            study.optimize(objective, timeout=self.timeout_sec)

            params = study.best_trial.params
            fam = params.pop("model_family")
            prep = params.pop("preprocessor", None)

            model_params = {k[len(fam) + 1 :]: v for k, v in params.items() if k.startswith(fam + "_")}
            prep_params = {
                k[len(prep) + 1 :]: v for k, v in params.items() if prep and k.startswith(prep + "_")
            }

            steps: list[tuple[str, Any]] = []
            if prep:
                prep_cls = PREPROCESSOR_CLASS_MAP.get(prep)
                if prep_cls:
                    steps.append(("preprocessor", prep_cls(**prep_params)))
            model_cls = MODEL_CLASS_MAP[fam]
            steps.append(("model", model_cls(**model_params)))
            self.best_pipeline = Pipeline(steps)
            self.best_pipeline.fit(X, y)
            self.best_score = study.best_value
            root.add(f"best-score: {self.best_score:.4f}")
        except ModuleNotFoundError as e:
            logger.warning("[%s] library missing – fallback LinearRegression: %s", self.__class__.__name__, e)
            from sklearn.linear_model import LinearRegression

            linreg = LinearRegression()
            linreg.fit(X, y)
            self.best_pipeline = Pipeline([("model", linreg)])
            self.best_score = linreg.score(X, y)

        console.print(root)
        logger.info("[%s] search-end", self.__class__.__name__)
        return self.best_pipeline

    def predict(self, X: pd.DataFrame) -> pd.Series:
        if self.best_pipeline is None:
            raise RuntimeError("Model not fitted. Call fit() first.")
        return self.best_pipeline.predict(X)

    def export(self, path: Path):
        if self.best_pipeline is None:
            raise RuntimeError("Model not fitted. Call fit() first.")

        model_file = path / "model.pkl"
        with open(model_file, "wb") as f:
            pickle.dump(self.best_pipeline, f)
        logger.info("[%s] Saved model pickle to %s", self.__class__.__name__, model_file)


__all__ = ["OptunaEngine"]
