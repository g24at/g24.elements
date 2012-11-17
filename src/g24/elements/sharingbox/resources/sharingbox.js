(function ($) {

    var EDIT = 0;
    var ADD = 1;

    var shbx_last_context = null;
    
    var shbx_lock   = 0;  // lock-counter to prevent multiple loading of sharingboxes
    var shbx_dirty  = 0;  // isDirty marker, set in onchange-handlers 

    var shbx_save_selector   = 'input#input-sharingbox_add_edit-form-controls-save';
    var shbx_cancel_selector = 'input#input-sharingbox_add_edit-form-controls-cancel';

    /* TOols
     * */

    function default_value(arg, def) {
        /* Add default parameter to argument */
        return typeof arg !== 'undefined' ? arg : def;
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
        if (! confirm_unload()) { return; }
        
        // set "create lock" 
        shbx_lock++;
        
        sharingbox_remove();
        
        restore_last_context();
        var context = $(linkel).closest('article');
        var context_id = context.attr('id');
        shbx_last_context = context_id;

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
                        context.after('<ul id="sharingbox_ul_wrapper" class="threadview"><li id="sharingbox_li_wrapper"></li></ul>');
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

        /* fieldsets */
        function initialize_features(checkbox, fieldset) {
            if (checkbox.is(':checked') === false) { fieldset.hide(); }
            checkbox.change(function (event) { fieldset.toggle(); });
        }
        initialize_features(
            $('#input-sharingbox_add_edit-is_event'),
            $('.sharingbox-event')
        );


        var editor = new wysihtml5.Editor("input-sharingbox_add_edit-text", {
            parserRules:  wysihtml5_g24_rules,
            name:         'sharingbox',
            style:        true,
            toolbar:      null,
            autoLink:     true,
            parser:       wysihtml5.dom.parse || Prototype.K,
            composerClassName: "wysihtml5-editor",
            bodyClassName:     "wysihtml5-supported",
            stylesheets:  [portal_url + '/++resource++g24.elements/views.css', 
                           portal_url + '/++resource++g24.elements.sharingbox/sharingbox.css'], // use stylesheet for editor
            allowObjectResizing:  true,
            supportTouchDevices:  true
        });
        var wysihtml5_resize_iframe = function() {
            editor.composer.iframe.style.height = editor.composer.element.scrollHeight + "px";
        };
        editor.observe("load", function () {
            editor.composer.element.addEventListener("keyup", wysihtml5_resize_iframe, false);
            editor.composer.element.addEventListener("blur", wysihtml5_resize_iframe, false);
            editor.composer.element.addEventListener("focus", wysihtml5_resize_iframe, false);
            //$(this.composer.iframe).autoResize();
        });
        editor.observe("change", function(){shbx_dirty=1;});

        // TODO: TEMPORARY
        /*
        $('.datepicker').dateinput({
            format: 'yyyy-mm-dd', // display format
            change: function () {
                var isoDate = this.getValue('yyyy-mm-dd'); // backend format
                $("#backendValue").val(isoDate);
            }
        });
        //yafowil.datepicker.binder();
        */

        /* recurrenceinput */
        /* TODO: create yafowil.widget.recurrenceinput
         *       localization needs request and currenct lang.
         *       both need a zope view and are better handled in a dedicated
         *       widget */
        // $.tools.recurrenceinput.localize('${request/LANGUAGE}', ${view/translation});
        // TODO
        /*
        jQuery('#input-sharingbox_add_edit-recurrence').recurrenceinput({
            lang: 'en',
            readOnly: false,
            startField: '#input-sharingbox_add_edit-start',
            ajaxURL: document.baseURI + '@@json_recurrence'
        });
        */

        /* submit */
        $('#sharingbox>form').submit(function (event) {
            event.preventDefault();

            if (event.originalEvent.explicitOriginalTarget === jQuery(shbx_cancel_selector)[0]) {
                // CANCEL ACTION
                if (! confirm_unload()) { return; }
                sharingbox_remove();
                restore_last_context();
                return; 
            } 
            
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
        
        
        // autosuggest for tags
        autosuggest_transform_element($("textarea.autosuggest[name$='subjects']"));
        
        // autosuggest for timezone field
        autosuggest_transform_element($('input.autosuggest[name$="timezone"]'));
        
        // autosuggest for place field
        autosuggest_transform_element($('input[name$="location"]'),
                {
                    selectedItemProp: "n",
                    searchObjProps: "n",
                    selectedValuesProp:"n"
                });
    }
    
    /*
     * Dirty Input
     */
    function isInputDirty() { return (shbx_dirty > 0); }
    function confirm_unload() {
        if (isInputDirty()) {
            ret = confirm('Unsaved changes - really discard?');
            if (ret === true) { shbx_dirty = 0; }
            return ret;
        } else {
            return true;
        }
    }

    function restore_last_context() {
        if (shbx_last_context !== null) { $('#' + shbx_last_context).show(); }
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
            searchObjProps: "v",
            selectedValuesProp:"v",
            queryParam: "q",
            minChars: 1,
            resultsHighlight: true,
            keyDelay: 400,
            neverSubmit: true, // block submit through <return>key
            limitText:"No more selections allowed"
        };
            
        options = (typeof options !== 'undefined') ? $.merge(options, default_options) : default_options;

        if ( element.prop('nodeName').toLowerCase() != 'textarea') {
            // single value
            options.selectionLimit = 1;
            // options.selectionAdded = function(el) {};
        }
        
        // determine ajax endpoint
        classes = element.attr('class').split(/\s+/);
        var item;
        for (item in classes ) {
            if (classes[item].indexOf('autosuggest-vocabulary') != -1) {
                query_endpoint = classes[item].split('-').pop();       
            }
        }
        query_endpoint      = portal_url + '/@@vocabularies/' + query_endpoint;
        options.preFill     = element.attr('value').split("\n").join(",");

        elname  = element.attr('name');
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
                var item;
                for (item in tags) { 
                    if ((tagv = tags[item].trim()) !== '') { realtags.push(tagv); }
                }
                    
                // determine name/selector for the original formfield
                origname    = element.name.replace(/-_-/g,".").replace('as_values_','');  // recover orig. fieldname            
                origfield   = $('[name='+origname.replace(/\./g,"\\.")+']'); // escape dot in selector '.' 

                // set value to orig. field
                fieldvalue  = origfield.hasClass('single') ? realtags[0] : realtags.join("\n");
                origfield.attr('value', fieldvalue);    
            });
    }

}(jQuery));
