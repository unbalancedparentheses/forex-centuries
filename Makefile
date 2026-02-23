.PHONY: all build validate visualize clean

all: build validate visualize

build:
	python build.py

validate:
	python validate.py || [ $$? -eq 1 ]

visualize:
	python visualize.py

clean:
	rm -f data/derived/normalized/*.csv
	rm -f data/derived/analysis/*.csv
	rm -f charts/*.png
