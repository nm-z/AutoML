# Training Results

This document summarizes the current training runs executed with the AutoML harness. All orchestrations invoke the three engine wrappers—`auto_sklearn_wrapper`, `tpot_wrapper`, and `autogluon_wrapper`—as required by the project guidelines.

## Dataset 1 (D1)

A quick baseline using the built-in Ridge regression model produced the following metrics on an 80/20 split:

- **R²**: -0.8567
- **RMSE**: 0.0030
- **MAE**: 0.0023

These results serve as a simple reference for verifying the pipeline on the smallest dataset.

## Dataset 2 (D2)

The latest orchestrator attempt on Dataset 2 completed only with the AutoGluon engine due to environment issues with Auto-Sklearn and TPOT. AutoGluon achieved an **R² of 0.8383** on the holdout set.

Further work is required to run all three engines successfully on D2 and to record comprehensive cross‑validation metrics.
