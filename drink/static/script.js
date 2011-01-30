var startcode = function(data, status, req) {
   var sortable = $(".shoppingList ul");
   sortable.data('items', data.tasks);
   sortable.html('');
   var e = null;
   for(n=0; n<data.tasks.length; n++) {
        e = $('<li>'+data.tasks[n].text+'</li>');
        e.data('item', data.tasks[n].id);
        sortable.append(e);
   };
   sortable.shoppingList();
   jQuery.fx.off = false;
   $('.shoppingList').fadeIn(1000);
}

$(document).ready(
    function(){
        jQuery.fx.off = true;
        $('.shoppingList').fadeOut();
        $.ajax({url: "view",
            dataType: 'json',
            data: {format: "json"},
            success: startcode ,
        });
    }
);