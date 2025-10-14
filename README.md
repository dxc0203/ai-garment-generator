AI Garment Generator
This is an internal proof-of-concept application designed to automate the creation of standardized, on-model product imagery for e-commerce platforms. It uses a combination of local AI models to create a complete workflow from product photo to final marketing asset.

The system is built with a human-in-the-loop approach, ensuring quality control at critical stages while automating the repetitive tasks of spec sheet creation and image generation.

Features
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

# AI Garment Generator - Setup and Launch Instructions

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
