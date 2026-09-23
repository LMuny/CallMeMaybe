NAME = CallMeMaybe
UV = uv

run : install
	$(UV) run python - m src/

install :
	$(UV) sync

debug :
	python -m pdb src/__main__.py

clean :

lint :
