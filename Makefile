VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

.PHONY: run create_user

run: $(VENV)/bin/activate
	$(PYTHON) -m uvicorn main:app

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

create_user:
	$(PYTHON) utils/create_user.py