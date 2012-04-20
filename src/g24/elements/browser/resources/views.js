(function ($) {

    /*
     * SHARINGBOX INTEGRATION
     * */
    function sharingbox_inserter(linkel, event) {
        event.preventDefault();
        $('#sharingbox').remove(); // remove first any sharingbox instance
        //$(linkel).parent().parent().hide(); 
        $(linkel).parent().parent().load($(linkel).attr('href') + ' #sharingbox');

        /*
        $.ajax({
          dataType : 'html',
          data     : {},
          url      : $(linkel).attr('href'),
          success  : function(data) {
            $('#sharingbox').remove(); // remove first any sharingbox instance
            $(linkel).parent().parent().hide(); 
            $(linkel).parent().parent().append($(data).find('#sharingbox'));
          }
        });*/
    }

    $(document).ready(function() {
        $('a.sharingbox_edit').click(function(event){
          sharingbox_inserter(this, event);
        });
        $('a.sharingbox_add').click(function(event){
          sharingbox_inserter(this, event);
        });
    });

}(jQuery));
