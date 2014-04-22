PentatonicHero
==============

GuitarHero controller to MIDI pentatonic scale

https://github.com/calaldees/PentatonicHero

`git clone https://github.com/calaldees/PentatonicHero.git`

Me and some friends play in a geeky band. We always want to have some kind of visual hook, geeky gimmick or audience participation when we play live. 

We wanted to encourage people to pick up musical instruments and get rocking. You don't need years of training to play your first few notes and play with others. With a pentatonic scale, you can bash the keys in any order like a deranged gorilla and still have some semblance of music that sounds in key. 

_Pentatonic Hero_ was created so a live band could back
two participating audience members, armed with familar _Guitar Hero_ controllers, that solo against each other while the crowds cheer their favourite participant.


Setup
-----

### Requirements

* MIDI Synth installed
	* Preferably with a good guitar sound.
	* Free software synths 
		* [FluidSynth](http://en.wikipedia.org/wiki/FluidSynth)
			* linux `apt-get install qsynth`
			* osx `brew install fluidsynth` 
		* [Komplete Player](http://www.native-instruments.com/en/products/komplete/samplers/kontakt-5-player/) (I use Native Instruments 'Rock Guitar' bundled with their basic 'Komplete Elements' as this has simulated fret noise).
* Recommended Guitar Hero Controller connected to your PC
    * With PS2 USB adaptor
    * Directly with USB (Xbox 360 wired Guitar hero controller)

### Install

* `git clone https://github.com/calaldees/PentatonicHero.git`

#### Windows

* Install
	* [Python3](https://www.python.org/downloads/windows/)
	* [Pygame](http://www.pygame.org/download.shtml)
* Setup Virtual Midi port
	* ???

#### Osx

* Install [homebrew](http://brew.sh/) package manager
	* You may need to `brew install git` and other basic dev tools
* `make install_osx` This will install python3 and pygame

* Setup Virtual Midi port
    * Open `Audio MIDI Setup`
    * Window -> Show MIDI Window
    * ICA Driver -> Show Info
    * Add a new port `PentatonicHero` (the name is important for auto selecting the correct port)

#### Linux (Ubuntu)

* ???

### Controller Setup

(Skip this if you just want to try it with the keyboard)

* Run pentatonic hero with controller debugging enabled
	* `python3 pentatonic_hero.py --show_controls`
	* Observe the button numbers and axis for the pitch bend
* Edit `controlers.py` to make to your correct joystick and button setup

### Run

* Load your synth software and listen to the `PentatonicHero` midi port and select your rockin guitar sound
* `python3 pentatonic_hero.py`
* Rock the **** out!

### Options

* Multiple controllers
* Multiple channels

