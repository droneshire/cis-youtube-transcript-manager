PYTHON ?= python
PIP ?= pip
MAYBE_UV = uv
PIP_COMPILE = $(if $(MAYBE_UV),pip compile,uv pip-compile)
# -- INSTALL_SYSTEM_ARGS ?= "--system --break-system-packages"

# Core paths
LOG_PATH=$(PWD)/logs
SOURCE_PATH=$(PWD)/src
PACKAGES_PATH=$(PWD)/packages
PY_VENV=$(PWD)/venv
PY_SITE_PACKAGES=$(PY_VENV)/lib/python3.12/site-packages

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
	$(MAYBE_UV) $(PIP_COMPILE) --strip-extras --output-file=$(PACKAGES_PATH)/requirements-dev.txt $(PACKAGES_PATH)/base_requirements.in $(PACKAGES_PATH)/dev_requirements.in
	$(MAYBE_UV) $(PIP) install $(INSTALL_SYSTEM_ARGS) -r $(PACKAGES_PATH)/requirements-dev.txt

install_requirements:
	$(PIP) install --upgrade pip
	$(PIP) install pip-tools uv
	$(MAYBE_UV) $(PIP) install $(INSTALL_SYSTEM_ARGS) -r $(PACKAGES_PATH)/requirements.txt

format: isort
	$(RUN_PY_DIRECT) ruff check --fix $(shell $(PY_FIND_COMMAND))
	$(BLACK_CMD)

check_format_fast:
	$(RUN_PY_DIRECT) ruff check --diff $(shell $(PY_FIND_COMMAND))
	$(BLACK_CMD) --check --diff

check_format: check_format_fast
	echo "Format check complete"

mypy_mod:
	$(RUN_PY_DIRECT) mypy $(shell $(PY_MODIFIED_FIND_COMMAND)) --config-file $(MYPY_CONFIG) --namespace-packages

mypy:
	$(RUN_PY_DIRECT) mypy $(shell $(PY_FIND_COMMAND)) --config-file $(MYPY_CONFIG)

pylint_mod:
	$(RUN_PY_DIRECT) pylint $(shell $(PY_MODIFIED_FIND_COMMAND))

pylint:
	$(RUN_PY_DIRECT) pylint $(shell $(PY_FIND_COMMAND))

autopep8:
	autopep8 --in-place --aggressive --aggressive $(shell $(PY_FIND_COMMAND))

isort:
	isort $(shell $(PY_FIND_COMMAND))

lint: check_format_fast mypy_mod pylint_mod

lint_full: check_format mypy pylint

test:
ifdef TESTMODULE
	$(RUN_COVERAGE_PY) unittest test.$(TESTMODULE)
else
	$(RUN_COVERAGE_PY) unittest discover -s test -p *_test.py -v
endif

upgrade: install
	pip install --upgrade $$(pip freeze | awk '{split($$0, a, "=="); print a[1]}')
	pip freeze > $(PACKAGES_PATH)/requirements-dev.txt

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
	rm -rf $(PACKAGES_PATH)/requirements*.txt
	$(MAKE) clean_all_pycache

.PHONY: create_dirs init install format check_format mypy pylint autopep8 isort lint
.PHONY: test upgrade clean
# End Makefile
