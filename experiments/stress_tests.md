# Stress and Error Testing Results

The `run_stress_tests.sh` script exercises the orchestrator across all datasets and intentionally provides bad inputs.

## Edge Cases Observed

1. **Non-existent files** – Running the orchestrator with missing CSV paths causes the program to log an error and exit with status code 1.
2. **Multiple datasets** – Looping over all datasets in the `DataSets/` folder works as expected, automatically discovering predictor and target files for each subdirectory.
3. **Short runtime** – Executing with `--time 10` on Dataset 1 completes quickly but produces lower quality models. This verifies that extremely small budgets are handled without crashing.

Use `./run_stress_tests.sh` to reproduce these scenarios.
