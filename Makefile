
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

