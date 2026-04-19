.PHONY: install uninstall test clean lint format

install:
	pip install -e .

uninstall:
	pip uninstall soundit-cli -y

reinstall: uninstall install

test:
	python -m pytest tests/ -v

lint:
	flake8 soundit_cli/
	pylint soundit_cli/

format:
	black soundit_cli/
	isort soundit_cli/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

dist: clean
	python setup.py sdist bdist_wheel

publish: dist
	twine upload dist/*
