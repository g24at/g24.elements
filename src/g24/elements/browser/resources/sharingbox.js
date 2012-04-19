(function ($) {

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

    $(document).ready(function() {
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

        $('#sharingbox-fieldset-title').hide();
        $('#sharingbox-features-title').change(function(event){
            $('#sharingbox-fieldset-title').toggle();
        });
        $('#sharingbox-fieldset-event').hide();
        $(":date").dateinput({format: 'yyyy-mm-dd'});
        $('#sharingbox-features-event').change(function(event){
            $('#sharingbox-fieldset-event').toggle();
        });
        $('#sharingbox-fieldset-location').hide();
        $('#sharingbox-features-location').change(function(event){
            $('#sharingbox-fieldset-location').toggle();
        });

    });

}(jQuery));
