OS = $(shell uname -s)

help:
	# -- Pentatonic Hero --
	# install : Install Pentatic Hero
	# run     : Run Pentatonic Hero

run:
	python3 pentatonic_hero.py

install: $(OS)

# OSX installation
Darwin:
	brew install python3 sdl sdl_image sdl_mixer sdl_ttf portmidi
	pip3 install hg+http://bitbucket.org/pygame/pygame

# Linux installation
Linux:
	sudo apt-get install -y python3
