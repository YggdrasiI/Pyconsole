FOLDER=$(realpath .)
PYTHON_BIN?=$(shell which python3 || which python)

# To use subcommand output as file [ cat <(echo "Test") ]
SHELL=/bin/bash

DEBUG?=1

# Name of package
PACKAGE=pykeykit

# Position of package in this repo
SRC_PACKAGES=src

# Root dir for static data
DATA_DIR=$(SRC_PACKAGES)/$(PACKAGE)/

POETRY=$(PYTHON_BIN) -m poetry
POETRY_VENV=.venv

help:
	@echo -e "Todo\n" \
		"make install             -- Install dependencies in $(POETRY_VENV)\n" \
		"make build               -- Creates whl-file in ./dist\n" \
		"make run                 -- Starts program in virtual environment.\n" \
		"" \

# Install everything in virtual environment
install: pyproject.toml poetry.toml
	$(POETRY) install

build:
	$(POETRY) build

# Activates venv, but runs from its source folder
run: $(POETRY_VENV)
	$(POETRY_VENV)/bin/python3 -m $(PACKAGE)

#poetry_run: $(POETRY_VENV)
#	 $(POETRY) run python3 -m $(PACKAGE)

# Example usage with piping
play:
	echo "'cv20'" | ./.venv/bin/python3 -m pykeykit

play2:
	echo -e 'ph = readmf("joy6.mid") \n ph' | ./.venv/bin/python3 -m pykeykit \
	&& sleep 5 \
	&& echo 'stop()' | ./.venv/bin/python3 -m pykeykit

zyn:
	zynaddsubfx -l /usr/share/zynaddsubfx/examples/Synth.xmz -U -I alsa -O alsa

# ====================================================
clean:
	@echo "This will clean the following files:"
	@git clean -n -d .
	@echo "Continue?" && read RSS_READER_CLEAN \
		&& test -n "$${RSS_READER_CLEAN}" -a "$${RSS_READER_CLEAN}" != "no" \
		&& git clean -f -d .

$(POETRY_VENV):
	make install

md:
	python3 -m grip -b README.md

.PHONY: clean
