install:
	pip install --upgrade pip wheel setuptools
	poetry install

build:
	poetry build

publish:
	poetry publish

release:
	changelog-gen

isort:
	isort -y