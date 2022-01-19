.PHONY: tests begin

install:
	pip install --upgrade pip
	poetry install

setup-poetry-ci:
	pip install poetry==1.1.3
	poetry config settings.virtualenvs.create false

install-ci: install-poetry-ci install	

build:
	poetry build

publish:
	poetry publish

release:
	changelog-gen

isort:
	isort -y

check-style:
	flake8

tests:
	pytest --cov=begin

begin:
	begin $(target) $(namespace)
