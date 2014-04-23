
help:
	# -- Pentatonic Hero --
	# install_osx
	# install_linux

run:
	python3 pentatonic_hero.py

install_osx:
	brew install python3 sdl sdl_image sdl_mixer sdl_ttf portmidi
	pip3 install hg+http://bitbucket.org/pygame/pygame

insyall_linux:
	sudo apt-get install -y python3