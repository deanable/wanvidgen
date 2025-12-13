# Fix: Logging Module Name Collision

## Issue
The file `src/wanvidgen/logging.py` was shadowing Python's standard library `logging` module, causing `ModuleNotFoundError` and import conflicts.

## Solution
Renamed `src/wanvidgen/logging.py` to `src/wanvidgen/log_config.py` to avoid naming collision with Python's standard library.

## Changes Made

### 1. File Renamed
- **Old**: `src/wanvidgen/logging.py`
- **New**: `src/wanvidgen/log_config.py`

### 2. Updated Imports in the Following Files

#### Source Code
- `src/wanvidgen/main.py`
  - Changed: `from .logging import configure_logging, LogConfig`
  - To: `from .log_config import configure_logging, LogConfig`

#### Test Files
- `acceptance_test.py`
  - Changed: `from wanvidgen.logging import configure_logging, get_logger, LogConfig, set_log_level`
  - To: `from wanvidgen.log_config import configure_logging, get_logger, LogConfig, set_log_level`

- `example.py`
  - Changed: `from wanvidgen.logging import configure_logging, get_logger, LogConfig`
  - To: `from wanvidgen.log_config import configure_logging, get_logger, LogConfig`

- `test_logging_output.py`
  - Changed: `from wanvidgen.logging import configure_logging, get_logger, LogConfig`
  - To: `from wanvidgen.log_config import configure_logging, get_logger, LogConfig`

- `test_kv_format.py`
  - Changed: `from wanvidgen.logging import configure_logging, get_logger, LogConfig`
  - To: `from wanvidgen.log_config import configure_logging, get_logger, LogConfig`

- `test_custom_log_dir.py`
  - Changed: `from wanvidgen.logging import configure_logging, get_logger, LogConfig`
  - To: `from wanvidgen.log_config import configure_logging, get_logger, LogConfig`

- `test_log_levels.py`
  - Changed: `from wanvidgen.logging import configure_logging, get_logger, LogConfig, set_log_level`
  - To: `from wanvidgen.log_config import configure_logging, get_logger, LogConfig, set_log_level`

## Verification

### Acceptance Criteria Met ✓
1. `python -m wanvidgen` runs without `ModuleNotFoundError` ✓
2. Application starts successfully ✓
3. Standard library `import logging` works correctly in all modules ✓
4. Custom logging configuration works as expected ✓

### Testing Performed
1. Verified `python -m wanvidgen --help` displays help without errors
2. Verified `python -m wanvidgen --check-system` runs system compatibility check
3. Verified `python -m wanvidgen --gui` attempts to start GUI (gracefully fails without display)
4. Tested that both standard library `logging` and custom `log_config` can be imported together
5. Verified all test scripts import the new module name correctly

## Impact
- **Breaking Change**: Any external code importing from `wanvidgen.logging` must update to `wanvidgen.log_config`
- **No Functional Changes**: All logging functionality remains the same, only the module name changed
- **Improved Compatibility**: Eliminates shadowing of Python's standard library module
