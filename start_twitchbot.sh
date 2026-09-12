#!/bin/bash
if ! [ -d ".venv" ]; then
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements
fi
source .venv/bin/activate
echo ""
python3 main.py
deactivate
