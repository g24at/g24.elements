(function ($) {

    var EDIT = 0;
    var ADD = 1;
    var last_context=null;
    
    var shbx_lock   = 0;  // lock-counter to prevent multiple loading of sharingboxes
    var shbx_dirty  = 0;  // isDirty marker, set in onchange-handlers 

    /* TOols
     * */

    function default_value(arg, def) {
        /* Add default parameter to argument */
        return typeof arg !== 'undefined' ? arg : def;
    }

    function urlify(text) {
        /* based on:
           http://stackoverflow.com/questions/1500260/detect-urls-in-text-with-javascript
           http://www.codinghorror.com/blog/2008/10/the-problem-with-urls.html

           The following RegExp matches only URLs after an whitespace or
           newline character or at the beginning of the text. It doesn't match
           any URLs with preceding characters like: src="http://test nor URLs
           in parenthesis (http://...)

           ^(https?://[^\s]+)|[\s\n](https?://[^\s]+)
           */
        //var urlRegex = /[^"'](https?:\/\/[^\s<]+)/g;
        var urlRegex = /[^"']?(https?:\/\/[^\s<]+)/g;
        return text.replace(urlRegex, function (url) {
            if (url.substr(0, 5) === 'https') { urlnoprot = url.substr(9); }
            else { urlnoprot = url.substr(8); }
            var urlpart = url.substr(-4);
            if (urlpart === '.png' | urlpart === '.gif' | urlpart === '.jpg') {
                return '<img src="' + url + '"/>';
            } else {
                return '<a href="' + url + '">' + urlnoprot + '</a>';
            }
        });
    }


    /*
     * SHARINGBOX INTEGRATION
     * */

    function sharingbox_remove(keep_list) {
        keep_list = default_value(keep_list, false);
        $('#sharingbox').remove(); // first remove any sharingbox instance
        if (keep_list === false) {
            $('#sharingbox_li_wrapper').remove(); // apply on all matched elements
            $('#sharingbox_ul_wrapper').remove();
        } else {
            $('#sharingbox_li_wrapper').removeAttr('id');
            $('#sharingbox_ul_wrapper').removeAttr('id');
        }
    }

    function sharingbox_inserter(linkel, event, mode) {
        /* Insert sharingbox into content.
         *
         * @param linkel: The element, which caused invocation of this function.
         * @param event:  jQuery event fired on linkel.
         * @param mode:   0..EDIT, 1..ADD
         *
         * */
        event.preventDefault();

        // test for "create-lock" (prevent double creation)
        if (shbx_lock > 0 ) { return; }
        
        // test for dirty inputs
        if ( isInputDirty() ) {
            if ( ! confirm('Unsaved changes - really discard ?') ) { return; } 
        }
        
        // set "create lock" 
        shbx_lock++;
        
        sharingbox_remove();
        if (last_context !== null) { $('#' + last_context).show(); }

        var context = $(linkel).closest('article');
        var context_id = context.attr('id');
        last_context = context_id;

// replaced .get by .ajax
//        /* ajax get */
//        $.get($(linkel).attr('href'), function(data){
//            if (mode===ADD) {
//                if ($(context_id + ' ul').length) {
//                    /* Add (new element in existing subthread) */
//                    $(context_id + ' ul').before('<li id="sharingbox_li_wrapper"></li>');
//                } else {
//                    /* Add (mew subthread) */
//                    context.after('<ul id="sharingbox_ul_wrapper"><li id="sharingbox_li_wrapper"></li></ul>');
//                }
//                $('#sharingbox_li_wrapper').html($(data));
//            }
//            else {
//                context.hide();
//                context.after($(data));
//            }
//            sharingbox_init(context, mode);
//
//            // release lock
//            shbx_lock = 0;
//        });

        /* ajax get */
        $.ajax({
            url: $(linkel).attr('href'),
            success: function (data) {
                if (mode === ADD) {
                    if ($(context_id + ' ul').length) {
                        /* Add (new element in existing subthread) */
                        $(context_id + ' ul').before('<li id="sharingbox_li_wrapper"></li>');
                    } else {
                        /* Add (mew subthread) */
                        context.after('<ul id="sharingbox_ul_wrapper"><li id="sharingbox_li_wrapper"></li></ul>');
                    }
                    $('#sharingbox_li_wrapper').html($(data));
                }
                else {
                    context.hide();
                    context.after($(data));
                }
                sharingbox_init(context, mode);

                // init ok, release lock
                shbx_lock = 0;
            },
            error : function (data) {
                // err, release lock anyway
                shbx_lock = 0;
            }
        });
    }

    function sharingbox_enable() {
        $('a.sharingbox_edit').click(function (event) {
            sharingbox_inserter(this, event, EDIT);
        });
        $('a.sharingbox_add').click(function (event) {
            sharingbox_inserter(this, event, ADD);
        });
    }

    /*
     * SHARINGBOX FEATURES
     * */

    function sharingbox_init(context, mode) {
        /* Initialize the sharingbox
         *
         * @param context: JQuery context, in which the sharingbox will be created.
         * @param mode: 0..Edit, 1..Add
         * */

        /* wysiwyg */
        /*
        $('#sharingbox-facade-content').html($('#sharingbox-text').val());
        $('#sharingbox-facade-content').show();
        $('#sharingbox-text').hide();
        $('#sharingbox-facade-bold').click(function(event){
            event.preventDefault();
            document.execCommand('StyleWithCSS', false, false);
            document.execCommand('bold',false,null);
        });
        $('#sharingbox-facade-italic').click(function(event){
            event.preventDefault();
            document.execCommand('StyleWithCSS', false, false);
            document.execCommand('italic',false,null);
        });
        */
        /* urlify */
        /*
        var timeout;
          $('#sharingbox-facade-content').bind('textchange', function () {
          clearTimeout(timeout);
          var self = this;
          timeout = setTimeout(function () {
          $('#sharingbox-facade-content').html(
          urlify($('#sharingbox-facade-content').html())
          ); }, 1000);
        });
        */


        /* fieldsets */
        function initialize_features(checkbox, fieldset) {
            if (checkbox.is(':checked') === false) { fieldset.hide(); }
            checkbox.change(function (event) { fieldset.toggle(); });
        }
        initialize_features(
            $('#input-sharingbox_add_edit-features-is_title'),
            $('#fieldset-sharingbox_add_edit-features-title')
        );
        initialize_features(
            $('#input-sharingbox_add_edit-features-is_event'),
            $('#fieldset-sharingbox_add_edit-features-event')
        );

        /*$('#input-sharingbox_add_edit-features-base-text').wysihtml5();*/
        var editor = new wysihtml5.Editor("input-sharingbox_add_edit-features-base-text", {
            parserRules:  wysihtml5_g24_rules,
            name:         'sharingbox',
            style:        true,
            toolbar:      null,
            autoLink:     true,
            parser:       wysihtml5.dom.parse || Prototype.K,
            composerClassName: "wysihtml5-editor",
            bodyClassName:     "wysihtml5-supported",
            stylesheets:  ['/++resource++g24.elements.sharingbox/sharingbox.css'], // use stylesheet for editor
            allowObjectResizing:  true,
            supportTouchDevices:  true
        });
        editor.observe("load", function () {
            $(this.composer.iframe).autoResize();
        });
        editor.observe("change", function(){shbx_dirty=1;});

        $('.datepicker').dateinput({
            format: 'yyyy-mm-dd', // display format
            change: function () {
                var isoDate = this.getValue('yyyy-mm-dd'); // backend format
                $("#backendValue").val(isoDate);
            }
        });
        //yafowil.datepicker.binder();

        /* recurrenceinput */
        /* TODO: create yafowil.widget.recurrenceinput
         *       localization needs request and currenct lang.
         *       both need a zope view and are better handled in a dedicated
         *       widget */
        // $.tools.recurrenceinput.localize('${request/LANGUAGE}', ${view/translation});
        jQuery('#input-sharingbox_add_edit-features-event-recurrence').recurrenceinput({
            lang: 'en',
            readOnly: false,
            startField: '#input-sharingbox_add_edit-features-event-start',
            ajaxURL: document.baseURI + '@@json_recurrence'
        });

        /* submit */
        $('#sharingbox>form').submit(function (event) {
            event.preventDefault();
            
            // process autosuggest fields
            autosuggest_submit_handler(this);
            
            //$('#sharingbox-text').val($('#sharingbox-facade-content').html());
            var form_data = $('#sharingbox>form').serialize();
            var form_submit = $('#sharingbox>form input[type="submit"]');
            form_data += '&' + form_submit.attr('name') + '=' + form_submit.val();

            $.post(
                $('#sharingbox>form').attr('action'),
                form_data,
                function (data) {
                    if (mode === EDIT) { /* Edit */
                        context.replaceWith(data);
                        sharingbox_remove();
                    }
                    if (mode === ADD) { /* ADD */
                        $('#sharingbox_li_wrapper').html(data);
                        sharingbox_remove(true);
                    }
                    sharingbox_enable();
                }
            );
            
            shbx_dirty = 0; // submitted, reset dirty marker
        });
        
        // set onchange handlers
        $("#sharingbox>form input").change(function(){shbx_dirty=1;});
        $("#sharingbox>form select").change(function(){shbx_dirty=1;});
        
        $(window).on('beforeunload',function(){
            if ( isInputDirty() ) return false;
        });
        
        autosuggest_transform_element($("textarea.autosuggest"));
        autosuggest_transform_element($("input.autosuggest"));
    }
    
    /*
     * Dirty Input
     */
    function isInputDirty()
    {
        return (shbx_dirty > 0);
    }


    $(document).ready(function () {
        sharingbox_enable();
    });
    
    
    /*
     * Auto-Suggestion
     */
    function autosuggest_transform_element(element, options) {
    	var default_options = {
    		preFill:"",
    		selectedItemProp: "v",
    		searchObjProps: "name,v",
    		selectedValuesProp:"v",
    		queryParam: "q",
    		minChars: 1,
    		resultsHighlight: true,
    		keyDelay: 400,
    		neverSubmit: true, // block submit through <return>key
    		limitText:"No more selections allowed",
    	};
    		
    	options = (typeof options !== 'undefined') ? $.merge(options, default_options) : default_options;

    	if ( element.prop('nodeName').toLowerCase() != 'textarea') {
    		// single value
    		options.selectionLimit = 1;
    		// options.selectionAdded = function(el) {};
    	}
    	
    	// determine ajax endpoint
    	classes = element.attr('class').split(/\s+/);
    	for ( i in classes ) {
    		if (classes[i].indexOf('autosuggest-vocabulary') != -1) {
    			query_endpoint = classes[i].split('-').pop();		
    		}
    	}
    	query_endpoint 		= "http://localhost:9000/stream/@@sharingbox_edit/" + query_endpoint;
    	
    	options.preFill 	= element.attr('value').split("\n").join(",");

    	elname 	= element.attr('name');
    	newname = '_g-auto_' + elname; // create name for intermediate field
    	options.asHtmlID = elname.replace(/\./g,"-_-");  // set ID to reference orig. field later
    	autosuggest = $('<input type="text" name="' + newname + '"/>'); 
    	element.after(autosuggest); // add intermediate field

    	// remove original field, insert again as hidden field
    	element.remove();
    	autosuggest.after('<input type="hidden" class="'+(options.selectionLimit==1?'single':'')+'" name="' + element.attr('name') + '" value="' + element.attr('value') + '"/>');

    	// enable autosuggest for new field
    	autosuggest.autoSuggest( query_endpoint, options );
    }

    function autosuggest_submit_handler(form)
    {
    	$(".as-values").each(function(index,element) {
    			// perpare value (strip empty tags)
    			tags = element.value.split(',');
    			realtags = Array();
    			for ( i in tags ) { 
    				if ((tagv = tags[i].trim()) != '') { realtags.push(tagv); }
    			}
    				
    			// determine name/selector for the original formfield
    			origname 	= element.name.replace(/-_-/g,".").replace('as_values_','');  // recover orig. fieldname			
    			origfield 	= $('[name='+origname.replace(/\./g,"\\.")+']'); // escape dot in selector '.' 

    			// set value to orig. field
    			fieldvalue	= origfield.hasClass('single') ? realtags[0] : realtags.join("\n");
    			origfield.attr('value', fieldvalue);	
    		});
    }

}(jQuery));
