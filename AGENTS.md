# AGENT Instructions

## Core AutoML Engine Requirements

All AutoML orchestrations must always run using all three engine wrappers:
- `auto_sklearn_wrapper`
- `tpot_wrapper`
- `autogluon_wrapper`

These engines must be used together regardless of any other options or instructions.

## Pull Request Quality Standards

### CRITICAL RULES - IMMEDIATE PR REJECTION

1. **Never Remove Core Functionality Without Explicit Justification**
   - Do NOT remove component discovery logic (`MODEL_FAMILIES`, `PREP_STEPS`)
   - Do NOT remove working validation functions
   - Do NOT comment out or delete critical pipeline components
   - Any removal of existing functionality MUST include detailed justification and replacement

2. **Documentation Must Match Reality**
   - PR descriptions MUST accurately reflect what the code actually does
   - If PR claims to "add tests" it must actually add tests, not remove them
   - If PR claims to "fix" something, it must actually fix it, not break it
   - False or misleading PR descriptions result in immediate closure

3. **No Breaking Changes Without Migration Path**
   - Do NOT introduce undefined variables or remove required imports
   - Do NOT change function signatures without updating all callers
   - Test that the orchestrator actually runs after your changes
   - Breaking changes require clear migration documentation

4. **Test Coverage Must Not Decrease**
   - Do NOT delete test files without replacing them with better tests
   - New functionality MUST include corresponding tests
   - Modified functionality MUST have tests updated accordingly
   - Test removals require explicit justification and approval

### SETUP SCRIPT RULES

5. **No Duplicated Logic in setup.sh**
   - Environment creation functions must not be duplicated
   - Installation steps must not be repeated
   - Each environment (env-as, env-tpa) created exactly once
   - Clear, linear flow without redundant operations

6. **Dependency Installation Must Be Robust**
   - Handle Python version compatibility explicitly
   - Auto-sklearn installation must check Python version compatibility
   - Use appropriate package installation flags (--prefer-binary, --only-binary)
   - Clear error messages for incompatible configurations

### CODE QUALITY REQUIREMENTS

7. **Component Discovery Must Remain Dynamic**
   - Keep automatic discovery of models and preprocessors
   - Do NOT hardcode component lists
   - Maintain extensibility for new components
   - Directory scanning logic must be preserved

8. **Validation Logic Must Be Comprehensive**
   - Component availability validation is REQUIRED
   - Early failure on missing components is MANDATORY
   - Clear error messages indicating exactly what is missing
   - No placeholder or no-op validation functions

9. **Error Handling Must Be Explicit**
   - Full tracebacks on exceptions as per workspace rules
   - Immediate pipeline termination on critical errors
   - No silent failures or ambiguous error states
   - Detailed logging at all major steps

### ORCHESTRATOR REQUIREMENTS

10. **CLI Interface Must Be Complete**
    - All required arguments properly validated
    - Help text must be accurate and comprehensive
    - Engine selection logic must be robust
    - Artifact generation must be guaranteed

11. **Cross-Validation Must Be Standardized**
    - 5×3 repeated cross-validation is MANDATORY
    - Consistent metric calculation across all engines
    - Hold-out set evaluation required
    - Results must be reproducible with fixed random seeds

12. **Artifact Management Must Be Consistent**
    - All outputs in 05_outputs/<dataset_name>/ structure
    - metrics.json generation is REQUIRED
    - Champion model persistence is MANDATORY
    - Comprehensive run metadata must be saved

### PR REVIEW CHECKLIST

Before submitting any PR, verify:
- [ ] Does the orchestrator import without errors?
- [ ] Do all existing tests still pass?
- [ ] Does `python orchestrator.py --help` work?
- [ ] Can component validation run successfully?
- [ ] Are there any undefined variables or missing imports?
- [ ] Does setup.sh run without duplicated operations?
- [ ] Is the PR description accurate and complete?
- [ ] Are any removed features explicitly justified?
- [ ] Do new features include appropriate tests?
- [ ] Is error handling comprehensive and explicit?

### AUTOMATIC CLOSURE CRITERIA

PRs will be immediately closed if they:
- Remove core component discovery without replacement
- Have false or misleading descriptions
- Delete tests without adding equivalent or better ones
- Introduce undefined variables or breaking changes
- Duplicate existing functionality without consolidation
- Replace working code with placeholder comments
- Remove validation logic without equivalent replacement
- Break the orchestrator's ability to run basic commands

### REVIEWER RESPONSIBILITIES

Reviewers must:
- Test that the orchestrator actually runs after PR changes
- Verify all claims in the PR description are accurate
- Check that no core functionality has been removed without justification
- Ensure test coverage has not decreased
- Validate that setup scripts work without duplication
- Confirm error handling remains comprehensive

## Summary

These rules exist because recent PRs have exhibited dangerous patterns:
- Removing working component discovery and replacing with undefined variables
- Claiming to add tests while actually deleting them
- Breaking core functionality while claiming to fix things
- Introducing duplicated setup logic
- Replacing robust validation with no-op placeholders

**Quality over speed. A working system is better than a broken "improved" one.**
