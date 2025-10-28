# AI Garment Generator - Standard Operating Procedures (SOP)

## Overview
This document outlines the Standard Operating Procedures (SOP) implemented to prevent and resolve common startup issues with the AI Garment Generator application.

## Preventive Measures Implemented

### 1. Enhanced Launcher Script (`start_app.bat`)
The launcher now includes comprehensive checks and automatic recovery procedures:

#### Pre-flight System Checks
- **Python Version Validation**: Ensures Python 3.11+ is installed and accessible
- **PATH Verification**: Confirms Python is properly added to system PATH
- **Version Compatibility**: Validates Python version meets minimum requirements

#### Virtual Environment Management
- **Integrity Checks**: Verifies virtual environment is not corrupted
- **Clean Install Option**: `--clean` flag for fresh environment setup
- **Automatic Recovery**: Handles common virtual environment issues

#### Package Management
- **Corruption Detection**: Automatically detects and removes corrupted packages
- **Version Validation**: Ensures critical packages are within compatible ranges
- **Automatic Recovery**: Reinstalls problematic packages when detected
- **Dependency Verification**: Confirms all required packages are properly installed

#### Health Checks
- **Import Testing**: Validates critical modules can be imported
- **Model Availability**: Checks OpenAI API connectivity and model access
- **Pre-launch Validation**: Ensures all components are ready before starting

### 2. Command Line Options
```bash
# Normal startup
start_app.bat

# Clean install (removes and recreates virtual environment)
start_app.bat --clean

# Update all packages to latest versions
start_app.bat --update

# Skip integrity checks (faster startup, less safe)
start_app.bat --skip-checks

# Force automatic recovery procedures
start_app.bat --force-recovery
```

### 3. Logging and Monitoring
- **Comprehensive Logging**: All operations logged to `logs/startup_YYYYMMDD_HHMMSS.log`
- **Error Tracking**: Detailed error messages with timestamps
- **Progress Tracking**: Step-by-step progress indicators
- **Troubleshooting Data**: Logs contain diagnostic information for issue resolution

## Common Issues and Solutions

### Issue: "Python is not installed or not added to PATH"
**Symptoms**: Launcher fails at step 1 with Python not found error
**Solutions**:
1. Install Python 3.11+ from https://python.org
2. Ensure Python is added to system PATH during installation
3. Restart command prompt and try again
4. Verify installation: `python --version`

### Issue: "Virtual environment creation failed"
**Symptoms**: Step 2 fails with virtual environment errors
**Solutions**:
1. Check available disk space
2. Run command prompt as administrator
3. Temporarily disable antivirus software
4. Use `--clean` flag to force fresh installation
5. Check for file permissions issues

### Issue: "Package corruption detected"
**Symptoms**: Warnings about corrupted packages during integrity checks
**Automatic Recovery**: The launcher will automatically attempt to fix corrupted packages
**Manual Solutions**:
1. Run: `python fix_corrupted_packages.py`
2. Use `--clean` flag for complete reinstall
3. Manually remove corrupted directories from `.venv\Lib\site-packages\`

### Issue: "Critical import test failed"
**Symptoms**: Step 6 fails with import errors
**Solutions**:
1. The launcher will attempt automatic recovery
2. If automatic recovery fails, use `--clean` flag
3. Manually reinstall problematic packages:
   ```bash
   pip install --force-reinstall streamlit protobuf openai
   ```

### Issue: "Model availability check failed"
**Symptoms**: Step 7 shows warnings about unavailable models
**Solutions**:
1. Check OpenAI API key in `.env` file
2. Verify internet connectivity
3. Check OpenAI account status and billing
4. Update model names in `app/constants.py` if needed

## Maintenance Procedures

### Regular Maintenance
1. **Weekly**: Run `start_app.bat --update` to keep packages current
2. **Monthly**: Run `start_app.bat --clean` for fresh environment
3. **As Needed**: Check logs in `logs/` directory for issues

### Log File Management
- Logs are automatically created in `logs/` directory
- Files are named: `startup_YYYYMMDD_HHMMSS.log`
- Review logs when issues occur
- Archive old logs periodically to save disk space

### Package Management
- **requirements.txt**: Contains pinned versions for stability
- **Automatic Updates**: Use `--update` flag for latest versions
- **Version Conflicts**: Check requirements.txt for compatibility issues

## Troubleshooting Workflow

### When Application Won't Start
1. **Check Logs**: Review the most recent log file in `logs/`
2. **Try Clean Install**: `start_app.bat --clean`
3. **Check Dependencies**: Ensure all prerequisites are installed
4. **Verify Environment**: Confirm no conflicting Python installations
5. **Network Issues**: Check internet connectivity for package downloads

### When Application Starts But Has Issues
1. **Model Issues**: Check OpenAI API key and connectivity
2. **Import Errors**: Run `python -c "import streamlit, google.protobuf, openai"`
3. **Database Issues**: Check `app.db` file permissions
4. **Port Conflicts**: Ensure port 8501 is available

### Emergency Recovery
If all else fails:
1. Delete `.venv` directory manually
2. Delete `app.db` if database corruption suspected
3. Run `start_app.bat --clean`
4. Check all prerequisites are met

## Key Files and Their Purposes

- `start_app.bat`: Main launcher with SOP measures
- `fix_corrupted_packages.py`: Detects and removes corrupted packages
- `check_models.py`: Validates OpenAI API connectivity
- `requirements.txt`: Defines package dependencies and versions
- `logs/*.log`: Contains detailed startup logs for troubleshooting

## Version Compatibility

### Supported Python Versions
- Minimum: Python 3.11.0
- Recommended: Python 3.11.x (latest patch version)
- Tested: Python 3.11.x

### Critical Package Versions
- Streamlit: 1.28.0 - 1.99.99
- Protobuf: 3.0.0 - 6.99.99
- OpenAI: 1.0.0 - 1.99.99

## Performance Optimization

### Fast Startup (Development)
```bash
start_app.bat --skip-checks
```

### Full Validation (Production)
```bash
start_app.bat
```

### Update Everything
```bash
start_app.bat --update
```

## Monitoring and Alerts

The launcher provides real-time feedback on:
- ✅ Successful operations
- ⚠️  Warnings (non-blocking issues)
- ❌ Errors (blocking issues)
- [SOP] Standard operating procedure recommendations

All operations are logged with timestamps for audit trails and debugging.

## Support and Escalation

If issues persist after following SOP procedures:
1. Collect the most recent log file from `logs/`
2. Note exact error messages and steps taken
3. Check system resources (disk space, memory)
4. Verify network connectivity
5. Consider environment-specific issues (corporate firewalls, antivirus)

---

**Last Updated**: October 26, 2025
**Version**: 2.0 - SOP Enhanced