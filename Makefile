.PHONY: tests begin

install:
	pip install --upgrade pip
	poetry install

ci-setup-poetry:
	pip install poetry==1.1.3
	poetry config settings.virtualenvs.create false

ci-install: ci-install-poetry install	

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
