var penatonic_hero = {};
(function(external, options){
	options = _.extend({
		inputs: 2,
        buttons: 5,
        track_length: 200,
	}, options) 

    var count = 0;
    
    // Init --------------------------------------------------------------------
    
    // Init button state arrays for all inputs
    var inputs = Array(options.inputs.length);
    for (var input_number=0 ; input_number < inputs.length ; input_number++) {
        inputs[input_number] = {} ; //Array(options.buttons);
        var button_states = inputs[input_number];
        for (var button_number=0 ; button_number < button_states.length ; button_number++) {
            button_states["button_"+button_number] = Array();
        }
        button_states['previous_active_button'] = null;
    }
    
    // Private -----------------------------------------------------------------
    
    function log_track_event(input, button_number, button_state) {
        /*
        The last button event is called active_note_track
        We store this because:
          - note_off dose not give us the button number
          - we only EVER play one note at once, so we always know the previous button is the one to disable
        */
        var _button_number = button_number;
        button_number = button_number || inputs[input]['previous_active_button'];
        inputs[input]['previous_active_button'] = _button_number;
        
        var track = inputs[input]["button_"+button_number];
        track.unshift({tick:count, state: button_state});
        if (_.last(track).tick < count + options.track_length) {
            track.pop();
        }
        return track;
    }
    
    function display_track(track) {
        var blocks = []
        return blocks;
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
        var event_handlers = {
            button_down: function(){
                $("#input"+data.input+"button"+data.button).addClass('button_on');  //document.getElementById('')
            },
            button_up: function() {
                $("#input"+data.input+"button"+data.button).removeClass('button_on');
            },
            note_on: function() {
                log_track_event(data.input, ""+data.button, 1);
            },
            note_off: function() {
                log_track_event(data.input, null, 0);
            },
        };
        if (_.has(event_handlers, data.event)) {
            event_handlers[data.event]();
        }
    };
    
    external.display = function() {
        /*
        Take the track timing info and return a set of block sizes to render on the display
        */
        var display = Array(options.inputs.length);
        for (var input_number=0 ; input_number < inputs.length ; input_number++) {
            display[input_number] = Array(button_states.length);
            for (var button_number=0 ; button_number < button_states.length ; button_number++) {
                display[input_number][button_number] = display_track(inputs[input]["button_"+button_number]);
            }
        }
        return display;
    };

}(penatonic_hero, options));
