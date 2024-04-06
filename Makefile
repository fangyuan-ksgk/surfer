
install:
	conda create -n surfer python=3.11 -y
	conda activate surfer

	brew install portaudio
	LDFLAGS="-L$(brew --prefix portaudio)/lib" CFLAGS="-I$(brew --prefix portaudio)/include" pip install pyaudio

	pip install -r requirements.txt

	pre-commit install
	pre-commit autoupdate

run:
	python -m main

run-pre-commit:
	pre-commit run --all-files
