
t: test
test:
	python -m pytest lully/ test/ -vv --doctest-modules


.PHONY: t test


fullrelease:
	echo -e "\n\n\n\n\n\n\nn\n\n\n\n" | fullrelease
