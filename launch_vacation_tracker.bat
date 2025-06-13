
cd /d "%~dp0"

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Run the Streamlit app
streamlit run vacation_tracker.py

:: Keep the window open if something fails
pause