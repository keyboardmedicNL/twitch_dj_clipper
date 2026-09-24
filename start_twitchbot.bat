@echo off
SETLOCAL
SET "VENV_DIR=%~dp0\.venv"

IF NOT EXIST "%VENV_DIR%\" (
	python -m venv .venv
	.venv\Scripts\activate
	pip install -r requirements
)

.venv\Scripts\activate
python main.py
deactivate
