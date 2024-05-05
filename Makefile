
install:
	# conda create -n surfer python=3.11 -y
	# conda activate surfer

	brew update
	brew upgrade
	# brew install ffmpeg
	brew install portaudio
	LDFLAGS="-L$(brew --prefix portaudio)/lib" CFLAGS="-I$(brew --prefix portaudio)/include" pip install pyaudio

	pip install -r requirements.txt

	playwright install

	pre-commit install
	pre-commit autoupdate

run:
	python -m main --mode 0 --type voice --continuous

run-pre-commit:
	pre-commit run --all-files
