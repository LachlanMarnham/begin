.PHONY: tests begin

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

check-style:
	flake8

tests:
	pytest --cov=begin

begin:
	@SETUPTOOLS_USE_DISTUTILS=stdlib poetry run begin $(target) $(namespace)
