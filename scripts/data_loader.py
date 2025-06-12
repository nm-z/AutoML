from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd
import importlib.util


def _ensure_parquet_engine() -> None:
    """Ensure that a Parquet engine is available."""
    if (
        importlib.util.find_spec("pyarrow") is None
        and importlib.util.find_spec("fastparquet") is None
    ):
        raise ImportError(
            "Loading Parquet files requires either 'pyarrow' or 'fastparquet'."
        )

def load_data(
    predictors_path: str | Path,
    target_path: str | Path,
    **kwargs
) -> Tuple[pd.DataFrame, pd.Series]:
    """Load predictor and target data from specified paths.

    Supports CSV and Parquet files. Parquet requires either ``pyarrow`` or
    ``fastparquet`` to be installed.

    Parameters
    ----------
    predictors_path : str | Path
        Path to the predictors data file (CSV or Parquet).
    target_path : str | Path
        Path to the target data file (CSV or Parquet).
    **kwargs
        Additional keyword arguments to pass to the underlying data loading function.

    Returns
    -------
    Tuple[pd.DataFrame, pd.Series]
        A tuple containing the features (X) as a DataFrame and the target (y) as a Series.

    Raises
    ------
    ValueError
        If the file format is unsupported or target file contains multiple columns.
    FileNotFoundError
        If the specified paths do not exist.
    """
    predictors_path = Path(predictors_path)
    target_path = Path(target_path)

    if not predictors_path.exists():
        raise FileNotFoundError(f"Predictors file not found: {predictors_path}")
    if not target_path.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")

    if predictors_path.suffix == ".csv":
        X = pd.read_csv(predictors_path, **kwargs)
    elif predictors_path.suffix == ".parquet":
        _ensure_parquet_engine()
        X = pd.read_parquet(predictors_path, **kwargs)
    else:
        raise ValueError(
            f"Unsupported predictors file format: {predictors_path.suffix}"
        )

    if target_path.suffix == ".csv":
        y = pd.read_csv(target_path, **kwargs).squeeze()
    elif target_path.suffix == ".parquet":
        _ensure_parquet_engine()
        y = pd.read_parquet(target_path, **kwargs).squeeze()
    else:
        raise ValueError(f"Unsupported target file format: {target_path.suffix}")

    if y.ndim > 1:
        raise ValueError("Target file must contain a single target column.")

    return X, y


__all__ = ["load_data"] 