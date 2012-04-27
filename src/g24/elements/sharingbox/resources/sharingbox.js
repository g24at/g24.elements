/*
 * SHARINGBOX FEATURES
 * */
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
    return text.replace(urlRegex, function(url) {
        if (url.substr(0,5) == 'https') { urlnoprot = url.substr(9); }
        else { urlnoprot = url.substr(8); }
        var urlpart = url.substr(-4);
        if (urlpart === '.png' | urlpart === '.gif' | urlpart === '.jpg') {
            return '<img src="' + url + '"/>';
        } else {
            return '<a href="' + url + '">' + urlnoprot + '</a>';
        }
    });
}

function sharingbox_init() {
    (function ($) {
        /* wysiwyg */
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

        /*var timeout;
          $('#sharingbox-facade-content').bind('textchange', function () {
          clearTimeout(timeout);
          var self = this;
          timeout = setTimeout(function () {
          $('#sharingbox-facade-content').html(
          urlify($('#sharingbox-facade-content').html())
          ); }, 1000);
          });*/

        /* fieldsets */
        if ($('#input-sharingbox_add_edit-features-is_thread').is(':checked') === false) {
            $('#fieldset-sharingbox_add_edit-features-title').hide();
        }
        $('#input-sharingbox_add_edit-features-is_thread').change(function(event){
            $('#fieldset-sharingbox_add_edit-features-title').toggle();
        });

        if ($('#input-sharingbox_add_edit-features-is_event').is(':checked') === false) {
            $('#fieldset-sharingbox_add_edit-features-event').hide();
        }
        $('#input-sharingbox_add_edit-features-is_event').change(function(event){
            $('#fieldset-sharingbox_add_edit-features-event').toggle();
        });

        if ($('#input-sharingbox_add_edit-features-is_location').is(':checked') === false) {
            $('#fieldset-sharingbox_add_edit-features-location').hide();
        }
        $('#input-sharingbox_add_edit-features-is_location').change(function(event){
            $('#fieldset-sharingbox_add_edit-features-location').toggle();
        });

        if ($('#input-sharingbox_add_edit-features-is_organizer').is(':checked') === false) {
            $('#fieldset-sharingbox_add_edit-features-organizer').hide();
        }
        $('#input-sharingbox_add_edit-features-is_organizer').change(function(event){
            $('#fieldset-sharingbox_add_edit-features-organizer').toggle();
        });


        /* submit */
        $('#sharingbox>form').submit(function(event){
            event.preventDefault();
            //$('#sharingbox-text').val($('#sharingbox-facade-content').html());
            var form_data = $('#sharingbox>form').serialize();
            var form_submit = $('#sharingbox>form input[type="submit"]');
            form_data += '&' + form_submit.attr('name') + '=' + form_submit.val();

            $.post(
                $('#sharingbox>form').attr('action'),
                form_data,
                function(data) {
                    alert('done!' + data);
                }
            );
        });

    }(jQuery));
}
