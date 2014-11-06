var penatonic_hero = {};
(function(external, options){
	options = _.extend({
		inputs: 2,
        buttons: 5,
        track_length: 200,
	}, options) 

    var count = 0;
    var active_note_track = null;
    
    // Init button state arrays for all inputs
    var inputs = Array(options.inputs.length);
    for (var input_number=0 ; input_number < inputs.length ; input_number++) {
        inputs[input_number] = Array(options.buttons);
        var button_states = inputs[input_number];
        for (var button_number=0 ; button_number < button_states.length ; button_number++) {
            button_states[button_number] = Array();
        }
    }
    
    external.tick = function() {
        count++;
    }
    
    external.event = function(data) {
        var event_handlers = {
            button_down: function(){
                $('#button'+data.button).addClass('button_on');
            },
            button_up: function() {
                $('#button'+data.button).removeClass('button_on');
            },
            /*
            note_on: function() {
                var track = inputs[data.input][data.button];
                track.unshift(count);
                if (_.last(track) < count + options.track_length) {
                    track.pop();
                }
                active_note_track = data.button;
            },
            note_off: function() {
                var track = inputs[data.input][active_note_track];
                track.unshift(count);
                active_note_track = null;
            },
            */
        };
        if (_.has(event_handlers, data.event)) {
            event_handlers[data.event]();
        }
    }

}(penatonic_hero, options));
