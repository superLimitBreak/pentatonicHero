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
	brew install python3 sdl sdl_image sdl_mixer sdl_ttf portmidi mercurial
	pip3 install hg+http://bitbucket.org/pygame/pygame

# Linux installation
Linux:
	# There is no python3-pygame package - The Pygame wiki suggests compileing it yourself.
	# http://www.pygame.org/wiki/CompileUbuntu
	sudo apt-get install -y python3 mercurial python3-dev python3-pip python3-numpy libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libsdl1.2-dev  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev
	pip3 install hg+http://bitbucket.org/pygame/pygame
	#hg clone https://bitbucket.org/pygame/pygame
	#cd pygame ; python3 setup.py build ; sudo python3 setup.py install
