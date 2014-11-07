var penatonic_hero = {};
(function(external, options){
	// Variables ---------------------------------------------------------------
	options = _.extend({
		inputs: 2,
		buttons: 5,
		track_length: 200,
	}, options) 

	var count = 0;

	// Private Class's ---------------------------------------------------------

	var ButtonState = function() {
		this.init();
		var track = Array();
		this.getTrack = function() {return this.track;}
	};
	ButtonState.prototype = {
		init: function() {
			//this.previousActiveButton = null;
			//this.meth()
		},
		addStateEvent: function(button_state) {
			this.getTrack().unshift({tick:count, state: button_state});
			if (_.last(this.getTrack()).tick < count + options.track_length) {
				this.getTrack().pop();
			}
		},
		getDisplayData: function() {
			
		}
	}
	
	var ButtonStates = function(){
		this.init();
		
		var previousActiveButton = null;
		this.setPreviousActiveButton = function(button_number) {previousActiveButton = button_number;}
		this.getPreviousActiveButton = function() {return previousActiveButton;}
		
		var tracks;
		this.clearTracks = function() {
			tracks = Array(options.buttons);
			for (var button_number=0 ; button_number < button_states.length ; button_number++) {
				tracks[button_number] = new ButtonState();
			}
		}
		this.getTrack = function(index) {return tracks[index];}
	}
	ButtonStates.prototype = {
		init: function() {
			this.clearTracks();
		},
		addStateEvent: function(button_number, button_state) {
			// Normalise input
			if (typeof(button_number) == "number") {button_number = ""+button_number;}  // Convert button integer to string so "0" is not boolean null
			
			// Remember previous active button
			var _button_number = button_number;
			button_number = button_number || this.getPreviousActiveButton();
			this.setPreviousActiveButton(_button_number);
			
			// Log event
			this.getTracks(button_number).addStateEvent(button_state);
		},
		getDisplayData: function() {
			
		},
		clearTracks: function() {
			this.clearTracks();
		}
	}

	// Init --------------------------------------------------------------------
	
	// Init button state arrays for all inputs
	var inputs = Array(options.inputs.length);
	for (var input_number=0 ; input_number < inputs.length ; input_number++) {
		  inputs[input_number] = new ButtonStates();
	}
	 
	// Private -----------------------------------------------------------------
	
	function display_track(track) {
		var blocks = []
		return blocks;
	}
	
	var event_handlers = {
		button_down: function(data) {
			this.arg // 1515
			$("#input"+data.input+"button"+data.button).addClass('button_on');  //document.getElementById('')
		},
		button_up: function(data) {
			$("#input"+data.input+"button"+data.button).removeClass('button_on');
		},
		note_on: function(data) {
			inputs[data.input].addStateEvent(data.button, 1);
		},
		note_off: function(data) {
			inputs[data.input].addStateEvent(null, 0);
		},
	}

	// Public ------------------------------------------------------------------
	
	external.tick = function() {
		var previous_count = count;
		count++;
		if (count < previous_count) {
			// reset all tracks
		}
	};
	
	external.event = function(data) {
		//this.arg = 1515
		if (_.has(event_handlers, data.event)) {
			event_handlers[data.event](data);
			//event_handlers[data.event].bind(this, 125)();  // bind, apply, call
		}
	};
	
	external.display = function() {
		var display = Array(options.inputs.length);
		for (var input_number=0 ; input_number < inputs.length ; input_number++) {
			display[input_number] = inputs[input_number].getDisplayData();
		}
		return display;
	};

}(penatonic_hero, options));
