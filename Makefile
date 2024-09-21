
## Create Conda environment
env:
	conda create -n surfer python=3.11 -y

## Install Python Dependencies
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
	ruff check src --fix
	ruff format src

## Run the application
run:
	# python -m main --mode 0 --type voice --continuous
	python -m src.main
	# python -m src.async_interaction_main

