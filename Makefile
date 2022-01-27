.PHONY: tests begin

# Done
install:
	pip install --upgrade pip
	poetry install

# Done
ci-setup-poetry:
	pip install poetry==1.1.3
	poetry config virtualenvs.create false

# Done
ci-install: ci-setup-poetry install	

# Done
build:
	poetry build

publish:
	poetry publish

release:
	changelog-gen

# Done
isort:
	isort -y

# Done
check-style:
	flake8

# Done
tests:
	pytest --cov=begin

ci-tests:
	pytest

ci-tests-with-coverage:
	pytest --cov=begin --cov-report=xml

begin:
	begin $(target) $(namespace)
