# Scripts Directory

This directory contains utility scripts for the AI Garment Generator application.

## Main Scripts

### `comprehensive_health_check.py`
**Purpose**: Comprehensive pre-launch health validation
- Checks pip functionality
- Validates package integrity (imports work)
- Validates package versions
- Automatically force reinstalls packages if any issues found
- Used by `start_app.bat` for pre-launch validation

### `force_reinstall_packages.py`
**Purpose**: Force reinstall critical Python packages
- Uninstalls and reinstalls: streamlit, protobuf, openai, pandas, pillow
- Used when package corruption is detected

## Diagnostic Scripts

### `check_models.py`
**Purpose**: Validate AI model availability
- Checks if configured AI models are accessible
- Used during startup to warn about unavailable models

## Maintenance Scripts

### `fix_corrupted_packages.py`
**Purpose**: Detect and fix corrupted packages
- Attempts to identify and repair corrupted package installations

## Batch Files

### `diagnose.bat`
**Purpose**: Quick diagnostic script
- Runs basic checks for common issues
- Can be run independently for troubleshooting

### `fix_install.bat`
**Purpose**: Installation fix script
- Attempts to fix common installation issues

### `run_app.bat`
**Purpose**: Alternative application launcher
- Simplified launcher without full SOP checks

## Usage

Most scripts are called automatically by `start_app.bat`. For manual usage:

```bash
# Run comprehensive health check
python scripts/comprehensive_health_check.py

# Force reinstall packages
python scripts/force_reinstall_packages.py

# Quick diagnostics
scripts\diagnose.bat
```

## Notes

- Scripts in this directory are designed to be run from the project root
- Some scripts create temporary files for inter-process communication
- All scripts include proper error handling and logging