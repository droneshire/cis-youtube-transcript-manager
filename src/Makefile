PYTHON ?= python3
PIP ?= pip3
MAYBE_UV = uv
PIP_COMPILE = $(if $(MAYBE_UV),pip compile,uv pip-compile)
# -- INSTALL_SYSTEM_ARGS ?= "--system --break-system-packages"

# Core paths
LOG_PATH=$(PWD)/logs
SOURCE_PATH=$(PWD)/src
PACKAGES_PATH=$(PWD)/packages
PY_VENV=$(PWD)/venv
PY_SITE_PACKAGES=$(PY_VENV)/lib/$(shell $(PYTHON) -c 'import sys; print("python{}.{}".format(sys.version_info[0], sys.version_info[1]))')/site-packages

PY_PATH:=$(SOURCE_PATH)

RUN_PY_DIRECT:=PYTHONPATH="$(PY_PATH)" $(PYTHON) -m
RUN_PY:=$(RUN_PY_DIRECT)
RUN_COVERAGE_PY:=PYTHONPATH="$(PY_PATH)" coverage run -m

# NOTE: exclude any virtual environment subdirectories here
PY_VENV_REL_PATH=$(subst $(PWD)/,,$(PY_VENV))
PY_FIND_COMMAND = find . -name '*.py' | grep -vE "($(PY_VENV_REL_PATH))"
PY_MODIFIED_FIND_COMMAND = git diff --name-only HEAD | grep '\.py$$' | grep -vE "($(PY_VENV_REL_PATH))"
# Consolidated mypy config to pyproject.toml
MYPY_CONFIG=$(SOURCE_PATH)/mypy_config.ini

BLACK_CMD = $(RUN_PY_DIRECT) black --line-length 100 $(shell $(PY_FIND_COMMAND))

create_dirs:
	mkdir -p $(LOG_PATH)

init: create_dirs
	@if [ -d "$(PY_VENV_REL_PATH)" ]; then \
		echo "\033[33mVirtual environment already exists\033[0m"; \
	else \
		$(PYTHON) -m venv $(PY_VENV_REL_PATH); \
	fi
	@echo "\033[0;32mRun 'source $(PY_VENV_REL_PATH)/bin/activate' to activate the virtual environment\033[0m"

install:
	$(PIP) install --upgrade pip
	$(PIP) install pip-tools uv
	$(MAYBE_UV) $(PIP_COMPILE) --strip-extras --output-file=$(PACKAGES_PATH)/requirements.txt $(PACKAGES_PATH)/requirements.in
	$(MAYBE_UV) pip install $(INSTALL_SYSTEM_ARGS) -r $(PACKAGES_PATH)/requirements.txt

format: isort
	$(RUN_PY_DIRECT) ruff check --fix $(shell $(PY_FIND_COMMAND))
	$(BLACK_CMD)

check_format:
	$(RUN_PY_DIRECT) ruff check --diff $(shell $(PY_FIND_COMMAND))
	$(BLACK_CMD) --check --diff

mypy:
	$(RUN_PY_DIRECT) mypy $(shell $(PY_FIND_COMMAND)) --config-file $(MYPY_CONFIG)

pylint:
	$(RUN_PY_DIRECT) pylint $(shell $(PY_FIND_COMMAND))

autopep8:
	autopep8 --in-place --aggressive --aggressive $(shell $(PY_FIND_COMMAND))

isort:
	isort $(shell $(PY_FIND_COMMAND))

lint: check_format mypy pylint

test:
ifdef TESTMODULE
	$(RUN_COVERAGE_PY) unittest test.$(TESTMODULE)
else
	$(RUN_COVERAGE_PY) unittest discover -s test -p *_test.py -v
endif

upgrade: install
	$(PIP) install --upgrade $$($(PIP) freeze | awk '{split($$0, a, "=="); print a[1]}')
	$(PIP) freeze > $(PACKAGES_PATH)/requirements.txt

clean_all_pycache:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -exec rm -f {} +

clean:
	rm -rf $(PY_VENV)
	rm -rf $(LOG_PATH)
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf dump.rdb
	rm -rf Makefile.flattened
	rm -rf $(PACKAGES_PATH)/requirements.txt
	rm -rf $(PWD)/dist
	rm -rf $(PWD)/build
	$(MAKE) clean_all_pycache

run_youtube_app:
	$(RUN_PY_DIRECT) streamlit run $(SOURCE_PATH)/executables/youtube_app.py

py_package:
	PYTHONPATH="$(PY_PATH)" $(PYTHON) -m PyInstaller $(PWD)/pyinstaller.spec --clean

copy_requirements:
	cp $(PACKAGES_PATH)/requirements.txt $(PWD)/requirements.txt

.PHONY: create_dirs init install format check_format mypy pylint autopep8 isort lint
.PHONY: test upgrade clean run_youtube_app py_package copy_requirements
# End Makefile
