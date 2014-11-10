var penatonic_hero = {};
(function(external, options){
	// Options ---------------------------------------------------------------
	options = _.extend({
		inputs: 2,
		buttons: 5,
		track_length: 200,
	}, options) 
	
	// Constants ---------------------------------------------------------------
	
	var BUTTON_NUMBERS = _.range(0, options.buttons);
	var INPUT_NUMBERS = _.range(0, options.inputs);
	
	// Variables ---------------------------------------------------------------
	
	var count = 0;

	// Private Class's ---------------------------------------------------------

	var ButtonState = function() {
		this.init();
		var track = Array();
		this.getTrack = function() {return track;}
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
			return this.getTrack();
		}
	}
	
	var ButtonStates = function(){
		//this.init();
		
		var previousActiveButton = null;
		this.setPreviousActiveButton = function(button_number) {previousActiveButton = button_number;}
		this.getPreviousActiveButton = function() {return previousActiveButton;}
		
		var tracks;
		this.clearTracks = function() {
			tracks = Array(options.buttons);
			for (var button_number=0 ; button_number < options.buttons ; button_number++) {
				tracks[button_number] = new ButtonState();
			}
		}
		this.clearTracks();
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
			
			// Record event in a track timestamp log
			this.getTrack(button_number).addStateEvent(button_state);
		},
		getDisplayData: function() {
			return _.map(BUTTON_NUMBERS, function(button_number){return this.getTrack(button_number).getDisplayData()});
		},
		//clearTracks: function() {
			//this.clearTracks();
		//}
	}

	// Init --------------------------------------------------------------------
	
	// Init button state arrays for all inputs
	var inputs = _.map(INPUT_NUMBERS, function(input_number){return new ButtonStates();});
	 
	// Private -----------------------------------------------------------------
	
	function display_track(track) {
		var blocks = []
		return blocks;
	}
	
	var event_handlers = {
		button_down: function(data) {
			this.arg; // 1515
			$("#input"+data.input+"button"+data.button).addClass('button_on');  //document.getElementById('')  // lookup vanilla js way of doing this
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
		data.input = data.input - 1;
		if (_.has(event_handlers, data.event)) {
			event_handlers[data.event](data);
			//event_handlers[data.event].bind(this, 125)();  // bind, apply, call
		}
	};
	
	external.display = function() {
		return _.map(INPUT_NUMBERS, function(input_number){inputs[input_number].getDisplayData();});
	};

}(penatonic_hero, {}));
