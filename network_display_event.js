var penatonic_hero = {};

(function(external, options) {

  // Options -----------------------------------------------------------------

  options = _.extend({
    inputs: 2,
    buttons: 5,
    track_length: 200,
    track_offscreen_length: 400,
  }, options);

  // Constants ---------------------------------------------------------------

  var BUTTON_NUMBERS = _.range(0, options.buttons);
  var INPUT_NUMBERS = _.range(0, options.inputs);

  // Variables ---------------------------------------------------------------

  var inputs;
  var count = 0;

  // Private Class's ---------------------------------------------------------

  var Track = function(options) {

    this.options = _.extend({}, {
      trackLimit: 200,
      trackLength: 1000
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

        this.data = this.filter(tick);

      }

      return this;

    },

    filter: function(tick) {
      return _.filter(this.data, function(datum) {
        return datum.tick > tick - this.options.trackLength;
      }, this);
    },

    render: function(tick) {

      var displayData = [];

      // Would be more efficient to
      // compute this on a rolling
      // basis (in the add() method)

      _.each(this.data, function(datum) {

        var displayDatum;
        var start;
        var stop;

        if (datum.isDown) {

          start = Math.min(tick - datum.tick, this.options.trackLimit);
          stop = 0;

          if (start <= 0) {
            return;
          }

          displayDatum = {
            start: start,
            stop: stop
          };

          displayData.push(displayDatum);

        } else {

          displayDatum = _.last(displayData);

          if (!displayDatum) {
            return;
          }

          stop = Math.max(tick - datum.tick, 0);

          if (stop > this.options.limit || stop === displayDatum.start) {
            displayData.pop();
            return;
          }

          displayDatum.stop = stop;

        }

      }, this);

      return displayData;

    },

    reset: function() {
      this.data = [];
    }

  };

  var Button = function(options) {

    this.options = _.extend({}, {
      trackLimit: 200,
      trackLength: 1000
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

      this.track = new Track({
        trackLimit: this.options.trackLimit,
        trackLength: this.options.trackLength
      });

    }

  };

  var ButtonBoard = function(options) {

    if (_.isNumber(options)) {
      options = {
        numberOfKeys: options
      };
    }

    this.options = _.extend({}, {
      numberOfKeys: 5,
      trackLimit: 200,
      trackLength: 1000
    }, options);

    this.reset();

  };

  ButtonBoard.prototype = {

    noteOn: function(tick, keyIndex) {
      this.keys[keyIndex].noteOn(tick);
    },

    noteOff: function(tick) {
      this.each(function(key) {
        key.noteOff(tick);
      });
    },

    each: function(callback) {
      _.each(this.keys, callback, this);
      return this;
    },

    reset: function() {
      this.keys = [];
      for (var i = 0; i < this.options.numberOfKeys; i++) {
        this.keys.push(new Button({
          trackLimit: this.options.trackLimit,
          trackLength: this.options.trackLength
        }));
      }
    },

    render: function(tick) {
      var render = [];
      this.each(function(key) {
        render.push(key.render(tick));
      });
      return render;
    }

  };

  // Init --------------------------------------------------------------------

  for (var i = 0; i < INPUT_NUMBERS; i++) {
    inputs.push(new ButtonBoard());
  }

  // Private -----------------------------------------------------------------

  var event_handlers = {
    button_down: function(data) {
      this.arg; // 1515
      $("#input" + data.input + "button" + data.button).addClass('button_on'); //document.getElementById('')  // lookup vanilla js way of doing this
    },
    button_up: function(data) {
      $("#input" + data.input + "button" + data.button).removeClass('button_on');
    },
    note_on: function(data) {
      inputs[data.input].noteOn(count, data.button);
    },
    note_off: function(data) {
      inputs[data.input].noteOff(count);
    }
  };

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
    var displayData = [];
    for (var i = 0; i < INPUT_NUMBERS; i++) {
      displayData.push(inputs[i].render());
    }
    return displayData;
  };

}(penatonic_hero, {}));
