USER_NAME   := $(shell whoami)

export UV_CACHE_DIR           := /goinfre/$(USER_NAME)/.cache/uv
export UV_PROJECT_ENVIRONMENT := /goinfre/$(USER_NAME)/venvs/call-me-maybe

NAME = CallMeMaybe
UV   = uv

all: run

run: install
	$(UV) run python -m src

install:
	$(UV) sync

debug: install
	$(UV) run python -m pdb -m src

clean:
	rm -rf src/__pycache__ .mypy_cache

lint:
	$(UV) run mypy src

.PHONY: all run install debug clean lint
