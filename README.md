PentatonicHero
==============

GuitarHero controller to MIDI pentatonic scale

https://github.com/calaldees/PentatonicHero

`git clone https://github.com/calaldees/PentatonicHero.git`

Me and some friends play in a geeky band. We always want to have some kind of visual hook, geeky gimmick or audience participation when we play live. 

We wanted to encourage people to pick up musical instruments and get rocking. You don't need years of training to play your first few notes and play with others. With a pentatonic scale, you can bash the keys in any order like a deranged gorilla and still have some semblance of music that sounds in key. 

_Pentatonic Hero_ was created so a live band could back
two participating audience members, armed with familar _Guitar Hero_ controllers, that solo against each other while the crowds cheer their favourite participant.

Features
--------

* Multiple guitars (outputing to differnt midi channels)
* Hammer-on's and pull-off's (the velocity of the hit decreases each time)
* Pitch bending
* Scale transposing (using start select buttons). Keeps in key but allows the performer to reach a greater range of notes.
* Root note (key) selection (hold down all the note buttons and use start/select to shift root note)

Setup
-----

### Requirements

* MIDI Synth installed
	* Preferably with a good guitar sound.
	* Free software synths 
		* [FluidSynth](http://en.wikipedia.org/wiki/FluidSynth)
			* linux `apt-get install qsynth`
			* osx `brew install fluidsynth`
			* [windows](http://sourceforge.net/projects/qsynth/)
		* [Komplete Player](http://www.native-instruments.com/en/products/komplete/samplers/kontakt-5-player/) (windows and osx)
			* I use _Native Instruments_ 'Rock Guitar' bundled with their basic 'Kontact 5 Player' as this has simulated fret noise.

* Recommended _Guitar Hero_ Controller connected to your PC
    * With Playstation 2 USB adaptor and Playstation 2 wired guitars
    * Directly with USB (Xbox 360 wired Guitar hero controller)
    * Other guitar controllers? wireless?

### Install

Clone the repository with git

* `git clone https://github.com/calaldees/PentatonicHero.git`

#### Windows

* Install
	* [Python3](https://www.python.org/downloads/windows/)
	* [Pygame](http://www.pygame.org/download.shtml)
* Setup Virtual Midi port
	* ???
		* [VirtualMidiSynth](http://coolsoft.altervista.org/en/virtualmidisynth?page=99999999#download)
		* [loobe1](http://www.nerds.de/en/loopbe1.html)
	* Add a new port `PentatonicHero` (the name is important for auto selecting the correct port)

#### Osx

* Install [homebrew](http://brew.sh/) package manager
	* You may need to `brew install git` and other basic dev tools
* `make install` This will install python3 and pygame. [Reference](http://florian-berger.de/en/articles/installing-pygame-for-python-3-on-os-x)

* Setup Virtual Midi port
    * Open `Audio MIDI Setup`
    * Window -> Show MIDI Window
    * ICA Driver -> Show Info
    * Add a new port `PentatonicHero` (the name is important for auto selecting the correct port)

#### Linux (Ubuntu 13.10)

* `make install`
*  ???

### Midi Synth Setup

####Linux

I found LMMS to give the best results in Linux so far, 
so here are instuctions on setting it up:

##### Setup soundfont
	1. Download a decent distorted electric guitar sound font (an .*sf2* file)
    2. Open LMMS
    3. Click *Edit* > *Settings* > *Folder icon*
    4. Choose the *.sf2* file for "DEFAULT SOUNDFONT FILE"
    5. Exit settings

##### Set a soundfont instument
	1. You should see a *Song-Editor* window in LMMS, if not the grey icon under the "New Project" icon
	2. Remove all instruments from the *Song-Editor* window, right-click > remove
	3. From the *Instrument plugins* panel on the left, drag a drop the *Sf2 Player* into the *Song-Editor* window
	4. Click on the instrument and in the text area at the top enter "PentatonicHero"
	5. Click on the *midi* tab
	6. Click *ENABLE MIDI INPUT*

Now you should be set, make sure to keep LMMS open for the duration of using PentatonicHero.

### Controller Setup

#### Default keyboard keys

* Notes (q,w,e,r,t) [hold note button and strum to play note]
* Strum (spacebar)
* Transpose in scale (o,p)
* _(Hold all notes and then transpose+/- to change root_note on the fly)_
* _(Pitch bend not supported on keyboard)_

#### With controler

* Run _Pentatonic Hero_ with controller debugging enabled
	* `python3 pentatonic_hero.py --log_level 0`
	* Observe the button numbers and axis for the pitch bend
* Edit `controlers.py` to make to your correct joystick and button setup
	* Add a new `my_joy = _hero_control_factory(...)`
	* Run `pentatonic_hero.py --input_profile my_joy`

### Run

* Load your synth software and listen to the `PentatonicHero` midi port and select your rockin guitar sound
* `python3 pentatonic_hero.py`
* Rock the **** out!

### More Options

`python3 pentatonic_hero.py --help`
