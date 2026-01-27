
at: styling typing tqf


tqf: tq
tq:
	python -m pytest test/ lully -vv --doctest-modules --ff -m "not slow"
t: test
test:
	python -m pytest test/ lully -vv --doctest-modules --ff
styling:
	ruff check lully/ --ignore=E741,E701,F401,E402,F403,E731
p: typing
typing:
	mypy lully/ test/ --pretty --disable-error-code var-annotated --disable-error-code no-redef --disable-error-code import-untyped --implicit-optional --warn-unused-ignores  --check-untyped-defs


.PHONY: t tq test at


upload_on_pypi:
	- rm -rf dist/
	- python setup.py build sdist
	- python -m twine upload dist/*
	echo "ALL_PROXY=$$ALL_PROXY"

clean:
	- rm -rf dist build lully.egg-info */__pycache__ .pytest_cache .ruff_cache .mypy_cache
