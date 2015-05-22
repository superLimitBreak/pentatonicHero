var penatonic_hero = {};

//------------------------------------------------------------------------------
// Model
//------------------------------------------------------------------------------


(function(external, options) {
	// Constants ---------------------------------------------------------------

	var DEFAULT_NUMBER_OF_BUTTONS = 5;
	var DEFAULT_TRACK_LIMIT = 200;
	var DEFAULT_TRACK_LENGTH = 400;

	// Options -----------------------------------------------------------------

	options = _.extendOwn({
		inputs: 2,
		buttons: DEFAULT_NUMBER_OF_BUTTONS,
		trackLimit: DEFAULT_TRACK_LIMIT,
		trackLength: DEFAULT_TRACK_LENGTH,
	}, options);


	// Variables ---------------------------------------------------------------

	var inputs = [];
	var tick = 0;


	// Private Class's ---------------------------------------------------------

	var Track = function(options) {
		this.options = _.extendOwn({
			trackLimit: DEFAULT_TRACK_LIMIT,
			trackLength: DEFAULT_TRACK_LENGTH,
		}, options);
		this.reset();
	};

	Track.prototype = {
		add: function(tick, isDown) {
			var lastDatum = _.last(this.data);
			if (!lastDatum || lastDatum.tick <= tick) {
				this.data.push({
					tick: tick,
					isDown: isDown
				});
				this.filterExpired(tick);
			}
			//return this;
		},

		filterExpired: function(tick) {
			var tickExpire = (tick - this.options.trackLength);
			this.data = _.filter(this.data, function(datum) {
				return datum.tick > tickExpire;
			}, this);
		},
	
		render: function(tick) {
			/*
			>>> limit = 200;
			
			Block incomplete
			>>> count = 1000;
			>>> track = [{tick:975, isDown:true}];
			[{start:0, stop:25}]
			
			Block complete
			>>> count = 100
			>>> track = [{tick:50, isDown:true}, {tick:90, isDown:false}];
			[{start:10, stop:50}]
			
			High count
			>>> count = 1000;
			>>> track = [{tick:0, isDown:true}, {tick:100, isDown:false}, {tick:900, isDown:true}]
			[{start:0, stop:100}]
			
			Outside range - should never be displayed
			>>> count = 1000;
			>>> track = [{tick:100, isDown:true}, {tick:200, isDown:false}]
			[]
			
			Multiple blocks + incomplete block
			>>> count = 1000;
			>>> track = [{tick:750, isDown:true}, {tick:850, isDown:false}, {tick:900, isDown:true}]
			[{start:150, stop:200}, {start:0, stop:100}]
			*/
			var displayData = [];
			_.each(this.data, function(element, index, list) {
				var previous = _.last(displayData);
				if (!element.isDown && previous && !previous.start) {
					previous.start = tick - element.tick;
					return;
				}
				if (element.isDown) {
					displayData.push({
						stop: Math.min(tick - element.tick, this.options.trackLimit),
						start: 0,
					});
					return;
				}
			}, this);
			// Remove element entirely over out limit
			displayData = _.filter(displayData, function(element){
				return !(element.start >= this.options.trackLimit && element.stop >= this.options.trackLimit);
			}, this);
			return displayData;
		},

		reset: function() {
			this.data = [];
		}
	};

	// Button -----------------------------
	
	var Button = function(options) {
		this.options = _.extendOwn({
			trackLimit: DEFAULT_TRACK_LIMIT,
			trackLength: DEFAULT_TRACK_LENGTH,
		}, options);
		this.reset();
	};

	Button.prototype = {
		noteOn: function(tick) {
			if (!this.isDown) {
				this.track.add(tick, true);
				this.isDown = true;
			}
		},

		noteOff: function(tick) {
			if (this.isDown) {
				this.track.add(tick, false);
				this.isDown = false;
			}
		},

		render: function(tick) {
			return this.track.render(tick);
		},

		reset: function() {
			this.isDown = false;
			this.track = new Track(this.options);
		}
	};

	// ButtonBoard ---------------------------
	
	var ButtonBoard = function(options) {
		//if (_.isNumber(options)) {
		//	options = {
		//		numberOfButtons: options
		//	};
		//}
		this.options = _.extendOwn({
			numberOfButtons: DEFAULT_NUMBER_OF_BUTTONS,
			trackLimit: DEFAULT_TRACK_LIMIT,
			trackLength: DEFAULT_TRACK_LENGTH,
		}, options);
		this.reset();
	};

	ButtonBoard.prototype = {

		noteOn: function(tick, buttonIndex) {
			this.buttons[buttonIndex].noteOn(tick);
		},

		noteOff: function(tick) {
			// We only ever play one note at once
			// A note off event will end all notes but only one of them should be 'active'
			_.each(this.buttons, function(element, index, list) {
				element.noteOff(tick);
			}, this);
		},

		reset: function() {
			this.buttons = _.map(_.range(0, this.options.numberOfButtons), function(element, index, list){
				return new Button(this.options);
			}, this);
		},

		render: function(tick) {
			return _.map(this.buttons, function(element, index, list){
				return element.render(tick);
			}, this);
		}
	};


	// Init --------------------------------------------------------------------

	_.each(_.range(0, options.inputs), function(element, index, list){
		inputs.push(new ButtonBoard());
	}, this);


	// Public ------------------------------------------------------------------

	var event_handlers = {
		button_down: function(data) {
			//this.arg; // 1515
			//$("#input" + data.input + "button" + data.button).addClass('button_on'); //document.getElementById('')  // lookup vanilla js way of doing this
		},
		button_up: function(data) {
			//$("#input" + data.input + "button" + data.button).removeClass('button_on');
		},
		note_on: function(data) {
			inputs[data.input].noteOn(tick, data.button);
		},
		note_off: function(data) {
			inputs[data.input].noteOff(tick);
		}
	};
	external.event_handlers = event_handlers;

	external.tick = function() {
		var previous_tick = tick;
		tick++;
		// Handle integer overflow
		if (tick < previous_tick) {
			// TODO: reset all tracks
		}
	};

	external.getTick = function() {
		return tick;
	};

	external.event = function(data) {
		//this.arg = 1515
		data.input = data.input - 1;
		if (_.has(event_handlers, data.event)) {
			event_handlers[data.event](data);
			//event_handlers[data.event].bind(this, 125)();  // bind, apply, call
		}
	};

	external.display = function() {
		return _.map(inputs, function(element, index, list) {
			return element.render(tick);
		}, this);
	};

}(penatonic_hero, {}));



//------------------------------------------------------------------------------
// Visulisation 
//------------------------------------------------------------------------------

(function(external, options) {
	options = _.extendOwn({
		element_id: '#screen',
		inputs: 2,
		buttons: 5,
		trackLimit: 200,
	}, options);

	var CONTAINER_CLASS = 'pentatonic_hero';
	
	var $root;
	var tick_interval;

	// Build HTML ----------------

	function generatePlayerHTML(input_number) {
		var $input = $('<div/>').addClass('input input'+input_number);
		_.each(_.range(0, options.buttons), function(element, index, list){
			var $track = $('<div/>').addClass('track button'+element);
			var $button_track = $('<div/>').addClass('button_track')
			var $button = $('<div/>').addClass('button');
			$track.append($button_track);
			$track.append($button);
			$input.append($track);
		});
		return $input;
	}

	function buildHTML() {
		$root = $(options.element_id);
		$root.addClass(CONTAINER_CLASS); // This is shit. Have an inner div
		$root.empty();
		
		_.each(_.range(0, options.inputs), function(element, index, list){
			$root.append(generatePlayerHTML(element));
		});
	}

	// Render logic ------------------
	
	function displayTrack($track, track_data) {
		// Ensure the number of divs in the track match the number of data elements to display
		_.each(_.range($track.children().length, track_data.length), function() {
			$track.prepend($('<div/>'));
		});
		_.each(_.range(track_data.length, $track.children().length), function(element, index, list) {
			_.last($track.find('div')).remove();
		});
		
		$track = $($track.selector);
		var unit = $track.innerHeight() / options.trackLimit;
		function getY(tick) {
			return (options.trackLimit * unit) - ((options.trackLimit - tick) * unit);
		}
		_.each(track_data, function(element, index, list){
			$($track.children()[index]).css({
				height: ''+getY(element.stop)-getY(element.start)+'px',
				bottom: ''+getY(element.start)+'px',
			});
		});

	}
	
	function displayInput(input_data, input_number, list) {
		if (input_number==0) {return;}
		_.each(input_data, function(track_data, index, list){
			displayTrack(
				$('.'+CONTAINER_CLASS+' .input.input'+input_number+' .track.button'+index+' .button_track'),
				track_data
			);
		});
	}

	function display() {
		penatonic_hero.tick();
		_.each(external.display(), displayInput, this);
		window.requestAnimationFrame(display);
	}
	
	function getButton(data) {
		return $root.find('.input'+data.input + ' .button'+data.button);
	}
	
	_.extend(external.event_handlers, {
		button_down: function(data) {
			getButton(data).addClass('button_on');
		},
		button_up: function(data) {
			getButton(data).removeClass('button_on');
		},
	});
	
	// External ----------------------------------------------------------------
	
	external.buildHTML = buildHTML;
	external.generatePlayerHTML = generatePlayerHTML;
	
	external.start = function() {
		buildHTML();
		//if (tick_interval != null) {
		//	clearInterval(tick_interval);
		//}
		//tick_interval = setInterval(display, 100);
		window.requestAnimationFrame(display);
	};
	
}(penatonic_hero, {}));

window.requestAnimationFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame || window.msRequestAnimationFrame;

document.addEventListener("DOMContentLoaded", function() {
	//penatonic_hero.buildHTML();
	penatonic_hero.start();
});