.PHONY: tests begin

install:
	pip install --upgrade pip
	poetry install

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
