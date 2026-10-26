check_and_test: FORCE
	mypy power_grid --strict
	mypy test --strict
	python3 -m unittest 

lint: FORCE
	pylint power_grid/
	pylint test/

format: FORCE
	autopep8 -i power_grid/*.py
	autopep8 -i test/*.py
	autopep8 -i test/test_integration/*.py
FORCE: ;
