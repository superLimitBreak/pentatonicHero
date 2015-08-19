OS = $(shell uname -s)

#Specific Linux Distro
REL=$(shell lsb_release -a 2> /dev/null | grep "Distributor ID:" | sed 's|.*:.\(.*\)|\1|')

.PHONY: help
help:
	# -- Pentatonic Hero --
	# install : Install Pentatic Hero
	# run     : Run Pentatonic Hero


# Installation -----------------------------------------------------------------
.PHONY: install
install: $(OS) libs/network_display_event.py libs/pygame_midi_wrapper.py libs/music.py

# OSX installation
.PHONY: Darwin has-brew
has-brew:
	# Fails if homebrew is not installed
	which brew
Darwin: has-brew
	brew install python3 sdl sdl_image sdl_mixer sdl_ttf portmidi mercurial
	pip3 install hg+http://bitbucket.org/pygame/pygame


# Linux installation
.PHONY: Linux Debian Ubuntu apt-installation
Linux: $(REL)
Debian: apt-installation
Ubuntu: apt-installation
apt-installation:
	# There is no python3-pygame package - The Pygame wiki suggests compileing it yourself.
	# http://www.pygame.org/wiki/CompileUbuntu
	sudo apt-get install -y python3 mercurial python3-dev python3-pip python3-numpy libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libsdl1.2-dev  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev
	sudo pip3 install hg+http://bitbucket.org/pygame/pygame
	#hg clone https://bitbucket.org/pygame/pygame
	#cd pygame ; python3 setup.py build ; sudo python3 setup.py install

libs:
	mkdir libs
	touch __init__.py
libs/network_display_event.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/net/network_display_event.py --compressed -O
libs/pygame_midi_wrapper.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/pygame_midi_wrapper.py --compressed -O
libs/pygame_midi_output.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/pygame_midi_output.py --compressed -O
libs/music.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/music.py --compressed -O


# Run --------------------------------------------------------------------------
.PHONY: run test
run:
	python3 pentatonic_hero.py

test:
	python3 -m doctest -v *.py

