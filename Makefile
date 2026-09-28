NAME = CallMeMaybe
UV = uv

run : install
	$(UV) run python - m src/

install :
	$(UV) sync

debug :
	python -m pdb src/__main__.py

clean :
	rm -r src/__pychache__ .mypy_cache

lint :
	mypy -m src
