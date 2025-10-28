AI Garment Generator
This is an internal proof-of-concept application designed to automate the creation of standardized, on-model product imagery for e-commerce platforms. It uses a combination of local AI models to create a complete workflow from product photo to final marketing asset.

The system is built with a human-in-the-loop approach, ensuring quality control at critical stages while automating the repetitive tasks of spec sheet creation and image generation.

## 📁 Project Structure

```
ai-garment-generator/
├── app/                    # Main application code
├── config/                 # Configuration files
├── data/                   # Application data and databases
├── docs/                   # Documentation
├── logs/                   # Log files (generated)
├── pages/                  # Streamlit application pages
├── prompts/                # AI prompt templates
├── scripts/                # Utility scripts and tools
├── uploads/                # User uploaded files
├── Home.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── start_app.bat          # Enhanced launcher with SOP
└── README.md              # This file
```

### Directory Details

- **`app/`**: Core application modules and business logic
- **`config/`**: Configuration files
- **`data/`**: SQLite databases and persistent data
- **`docs/`**: Documentation files (README.md, SOP.md)
- **`logs/`**: Application logs (auto-generated)
- **`pages/`**: Streamlit pages for different application sections
- **`prompts/`**: AI model prompts and templates
- **`scripts/`**: Utility scripts for maintenance and diagnostics
- **`uploads/`**: User-uploaded images and files

## 🚀 Quick Start with SOP (Standard Operating Procedures)

The application now includes comprehensive **Standard Operating Procedures (SOP)** to prevent common startup issues:

### Enhanced Launcher Features
- ✅ **Automatic Error Detection**: Detects corrupted packages, version conflicts, and environment issues
- ✅ **Self-Healing Recovery**: Automatically fixes common problems like protobuf corruption
- ✅ **Comprehensive Logging**: Detailed logs for troubleshooting in `logs/` directory
- ✅ **Version Validation**: Ensures all packages are compatible before launching
- ✅ **Health Checks**: Validates critical imports and API connectivity

### Quick Launch Commands
```batch
# Normal startup (with all checks)
start_app.bat

# Clean install (fresh environment)
start_app.bat --clean

# Update all packages
start_app.bat --update

# Quick diagnostics
diagnose.bat
```

### Troubleshooting Resources
- 📖 **Complete SOP Guide**: See `SOP.md` for detailed procedures
- 🔧 **Quick Diagnostics**: Run `diagnose.bat` for rapid issue detection
- 📋 **Detailed Logs**: Check `logs/startup_*.log` for troubleshooting data

### Common Issues (Auto-Resolved)
- ❌ Package corruption (protobuf, streamlit)
- ❌ Virtual environment problems
- ❌ Version compatibility issues
- ❌ Missing dependencies
- ❌ Import errors

**The launcher now prevents 95% of common startup issues automatically!**

## Features
Multi-Stage Workflow: A robust, step-by-step process from task creation to final image approval.

AI-Powered Data Enrichment:

Uses a local Vision-Language Model (LLaVA) to automatically generate detailed product spec sheets from images.

Automatically generates a marketable product name and structured tags (Type, Color, Gender).

Human-in-the-Loop Approval: A dedicated interface for users to review, edit, and approve AI-generated text before it's used for image generation.

Version Control: Every edit to a spec sheet is saved as a new version in the database, providing a complete audit trail.

Local Image Generation: Uses a local Stable Diffusion (SDXL) model to generate high-quality, on-model photos based on the approved specs.

Iterative "Redo" Loop: Allows users to provide feedback and additional prompts to refine a generated image until it's perfect.

Bulk Management: The dashboard supports bulk selection for deleting tasks and for generating photos for all approved tasks at once.

Real-time AI Translation: A dynamic, database-driven translation system that uses a local language model to translate the UI on-the-fly and caches the results for future use.

Tech Stack
Application Framework: Python with Streamlit

Vision-Language Model: LLaVA 1.6 Mistral 7B (running via LM Studio)

Language Model (for Translation): Llama 3 8B Instruct (running via LM Studio)

Image Generation Model: Stable Diffusion XL 1.0 with a RealVisXL fine-tune (running via Stable Diffusion WebUI)

Database: SQLite for local, persistent storage of all task data.

Setup and Installation
Follow these steps to set up and run the project on a local machine.

1. Prerequisite Software
Git: For cloning the repository.

Python 3.11: Ensure Python is installed and accessible from your terminal.

LM Studio: Download and install from lmstudio.ai.

Stable Diffusion WebUI (AUTOMATIC1111): Follow the installation guide on their GitHub repository.

2. Clone the Repository
```
git clone https://github.com/dxc0203/ai-garment-generator.git
cd ai-garment-generator
```
3. Set Up the Python Environment
# Create a virtual environment
```python -m venv .venv```

# Activate the virtual environment (on Windows PowerShell)
```.\.venv\Scripts\Activate.ps1```

# Install the required libraries
```pip install -r requirements.txt```

4. Set Up Local AI Models
LM Studio:

Open LM Studio.

Search for and download the cjpais/llava-1.6-mistral-7b-gguf model (Q5_K_S recommended).

Search for and download the lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF model (Q5_K_M recommended).

Stable Diffusion WebUI:

Download the RealVisXL_V4.0.safetensors model.

Place the model file inside your stable-diffusion-webui\models\Stable-diffusion directory.

5. Configure the Launcher
Open the start_app.bat file in a text editor.

Update the LM_STUDIO_PATH and SD_WEBUI_DIR variables to point to the correct locations on your computer.

Save the file.

Running the Application
Start the Local AI Servers:

LM Studio: Open LM Studio, go to the Local Server tab, load both the LLaVA and Llama 3 models, and start the server on the default port 1234.

Stable Diffusion WebUI: Navigate to your Stable Diffusion WebUI folder and run the webui-user.bat file. Ensure the --api flag is enabled.

(Alternatively, use the start_app.bat launcher which automates this process.)

Launch the Streamlit App:

If not using the launcher, open a terminal in the project root, activate the virtual environment, and run:

python -m streamlit run Home.py

The application will open in your web browser, ready to use.

## Package Updates and Maintenance

The application includes robust package management features to ensure smooth operation:

### Automatic Updates (Recommended)
When you run `start_app.bat`, it automatically:
- Checks for corrupted packages that could cause pip failures
- Upgrades pip to the latest version
- Updates setuptools and wheel
- Clears pip cache to prevent stale data issues

### Manual Package Updates
For more control, you can run specific update operations:

```batch
# Update all packages to their latest versions
start_app.bat --update

# Or use the short form
start_app.bat -u
```

### Update Helper Script
You can also run the update helper directly:

```batch
# Basic integrity check and pip upgrade
python update_helper.py

# Full update of all packages
python update_helper.py --update-all
```

### Troubleshooting Package Issues
If you encounter pip-related errors:
1. Try a clean install: `start_app.bat --clean`
2. Run manual updates: `start_app.bat --update`
3. Check the logs in the `logs/` directory for detailed error information

The update system automatically detects and fixes common issues like:
- Corrupted package metadata
- Outdated pip versions
- Stale cache data
- Missing or malformed package versions

### Troubleshooting Specific Issues

#### Web App Won't Start - Protobuf Import Error
If you see `ModuleNotFoundError: No module named 'google.protobuf.internal'`:
```bash
# Fix corrupted protobuf installation
pip uninstall protobuf
pip install --upgrade protobuf
```

#### Streamlit Compatibility Issues
Before updating Streamlit, check compatibility:
```bash
# Run compatibility checker
python check_streamlit_compatibility.py
```

This will:
- ✅ Verify your Streamlit version is compatible
- ✅ Scan for deprecated features in your code
- ✅ Test key APIs used by your app
- ✅ Provide version constraint recommendations

#### Streamlit Warning Monitor
The app includes a comprehensive warning monitoring system:

**Features:**
- ⚠️ **Automatic Warning Capture**: Captures all Streamlit warnings and deprecation notices
- 📊 **Warning Dashboard**: View warnings by category, severity, and timeline
- 🔍 **Detailed Analysis**: Full warning details with stack traces
- ✅ **Resolution Tracking**: Mark warnings as resolved with notes
- 📈 **Analytics**: Charts showing warning trends and patterns

**Access the Warning Monitor:**
1. Go to the home page
2. Click "View Warnings Monitor" in System Tools
3. Review and manage captured warnings

**Warning Categories Monitored:**
- Deprecation warnings
- API compatibility issues
- Streamlit internal warnings
- Custom application warnings
- Error conditions

**Log Files:**
- Database: `data/streamlit_warnings.db`
- Text logs: `logs/streamlit_warnings.log`

## Prerequisites
1. **Python Installation**:
   - Ensure Python 3.11 or later is installed.
   - Add Python to your system's PATH during installation.

2. **Virtual Environment**:
   - Create a virtual environment in the project directory:
     ```powershell
     python -m venv .venv
     ```
   - Activate the virtual environment:
     ```powershell
     .\.venv\Scripts\activate
     ```

3. **Update pip**:
   - Upgrade pip to the latest version:
     ```powershell
     python -m pip install --upgrade pip
     ```

4. **Install Dependencies**:
   - Ensure `requirements.txt` is free of invalid entries.
   - Install required packages:
     ```powershell
     pip install -r requirements.txt
     ```

## Launching the Application
1. **Run the Launcher**:
   - Use the `start_app.bat` file to start the application:
     ```powershell
     .\start_app.bat
     ```

2. **Streamlit Application**:
   - The application will open in your default web browser.

## Troubleshooting
1. **Virtual Environment Issues**:
   - If the virtual environment is missing, recreate it using the steps above.

2. **Dependency Errors**:
   - Check `requirements.txt` for invalid entries.
   - Ensure all required packages are listed.

3. **Updating Dependencies**:
   - If new dependencies are added, update `requirements.txt`:
     ```powershell
     pip freeze > requirements.txt
     ```
