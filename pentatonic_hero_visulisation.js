var penatonic_hero = {};

(function(external, options) {
	options = _.extendOwn({
        element_id: 'screen',
        buttons: 5,
        trackLimit: 200,
	}, options);

    
    function generatePlayerHtml(player_number) {
        /* bollox  ... forget this just use jquery */
        style = ''
        style += '.note_area {width: 100%; height: 100%;}';
        style += '.button_area {height: 5%}'
        html = '<div class="note_area"></div>';
        _.each(_.range(0, options.buttons), function(element, index, list){
            
        });
        return ""
    }

    function buildHTML() {
        //document.getElementById(options.element_id).innerHTML = "";
    }
  
    function displayInput(input_data, index) {
        
    }
  
    function display() {
        penatonic_hero.tick();
        _.each(penatonic_hero.display(), displayInput);
    }
    
    // External ----------------------------------------------------------------
    
    external.buildHTML = buildHTML
    
}(penatonic_hero, {}));
