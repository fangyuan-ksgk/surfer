#################################################################################
# GLOBALS                                                                       #
#################################################################################


PROJECT_NAME = temus-linguaforge-surfer
PYTHON_VERSION = 3.11
PYTHON_INTERPRETER = python


#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
env:
	conda create -n surfer python=3.11 -y

install:
	brew update
	brew upgrade
	# brew install ffmpeg
	brew install portaudio
	LDFLAGS="-L$(brew --prefix portaudio)/lib" CFLAGS="-I$(brew --prefix portaudio)/include" pip install pyaudio

	poetry lock --no-update && poetry install --no-root
	pip install pyaudio

	playwright install


## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint
lint:
	mypy src
	ruff check src --fix
	ruff format src


## Run the application
run:
	python -m main --mode 0 --type voice --continuous


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################


.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)

