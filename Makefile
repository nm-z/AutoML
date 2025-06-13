PHONY += setup test clean

setup:
	@echo "Setting up the AutoML Harness environment (Python 3.11 only)..."
	@bash setup.sh
	@echo "Setup complete. Remember to activate your environment: ./activate.sh"

test:
	@echo "Running post-setup verification..."
	@bash setup.sh # Rerun setup.sh to trigger environment test
	# In a real scenario, you would have a `python -m pytest` or similar here

clean:
	@echo "Cleaning up generated files and environments..."
	@rm -rf env-tpa 05_outputs
	@find . -name "__pycache__" -exec rm -rf {} + || true
	@find . -name ".pytest_cache" -exec rm -rf {} + || true
	@echo "Cleanup complete." 