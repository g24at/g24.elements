(function ($) {

    /*
     * SHARINGBOX INTEGRATION
     * */
    var last_context=null;
    function sharingbox_inserter(linkel, event) {
        event.preventDefault();
        $('#sharingbox').remove(); // remove first any sharingbox instance
        var context = $(linkel).parent().parent();
        if (last_context !== null) { $('#'+last_context).show(); }
        last_context = context.attr('id');
        context.hide();
        $.get($(linkel).attr('href'), function(data){
            context.after($(data));
        });
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
