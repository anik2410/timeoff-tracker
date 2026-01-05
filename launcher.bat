@REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python to continue.
    pause
    exit /b 1
)
@REM If Python is installed, proceed with the installation
echo Python is installed.
:: If a virtual environment already exists, skip creation
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    :: Create a virtual environment
    python -m venv venv
    :: Activate the virtual environment
    call venv\Scripts\activate.bat
    :: Upgrade pip
    python -m pip install --upgrade pip
    :: Install required packages
    pip install -r requirements.txt
    echo Installation complete.
) ELSE (
    echo Virtual environment already exists. Skipping creation.
    :: Activate the virtual environment
    call venv\Scripts\activate.bat
)
:: IF .gitignore file does not exist, create it
IF NOT EXIST ".gitignore" (
    echo Creating .gitignore file...
    echo ./ > .gitignore
    echo __pycache__/ >> .gitignore
    echo *.pyc >> .gitignore
    echo *.pyo >> .gitignore
    echo *.pyd >> .gitignore
    echo *.db >> .gitignore
    echo *.txt >> .gitignore
    echo *.csv >> .gitignore
    echo venv/ >> .gitignore
    echo .gitignore file created.
)
:: Run the Streamlit app
start "" streamlit run main.py
exit /b 0
