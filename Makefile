.PHONY: all build validate visualize test clean help

all: build validate visualize

build:
	python build.py

validate:
	python validate.py; rc=$$?; [ $$rc -le 1 ] || exit $$rc

visualize:
	python visualize.py

test:
	pytest tests/ -v

clean:
	rm -f data/derived/normalized/*.csv
	rm -f data/derived/analysis/*.csv
	rm -f charts/*.png

help:
	@echo "Available targets:"
	@echo "  all        Build, validate, and visualize (default)"
	@echo "  build      Run build.py to regenerate derived data"
	@echo "  validate   Run validate.py data quality checks"
	@echo "  visualize  Run visualize.py to generate charts"
	@echo "  test       Run pytest test suite"
	@echo "  clean      Remove all derived CSVs and chart PNGs"
	@echo "  help       Show this help message"
