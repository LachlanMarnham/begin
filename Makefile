.PHONY: tests begin

install:
	pip install --upgrade pip
	poetry install

ci-setup-poetry:
	pip install poetry==1.1.3
	poetry config virtualenvs.create false

ci-install: ci-setup-poetry install	

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

ci-tests:
	pytest --cov=changelog_gen --cov-report=xml

begin:
	begin $(target) $(namespace)
