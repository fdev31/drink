var startcode = function(data, status, req) {
   var sortable = $(".sortable");
   sortable.data('items', data.items);
   data.items.length;
   sortable.html('');
   var i;
   var url_regex = /^(\/|http).+/;

   for(n=0; n<data.items.length; n++) {
        i = data.items[n];

        var mime = "";
        if ( i.mime ) {
            if ( i.mime.match( url_regex )) {
                mime = i.mime;
            } else {
                mime = "/static/mime/"+i.mime+".png";
            }
        } else {
            mime = "/static/mime/page.png";
        }
        e = $('<li class="entry"><a href="'+i.path+i.id+'/edit"><img width="32px" src="'+mime+'" /></a><a href="'+i.path+i.id+'/view">'+(i.title || i.id)+'</a></li>');
        e.data('item', i.id);
        e.disableSelection();
        sortable.append(e);
   }
   sortable.sortable({
        axis: "y",
        containment: ".sortable",
        distance: 10,
   });
}


$(document).ready(
    function(){
        //jQuery.fx.off = true;
        //$('.shoppingList').fadeOut();
        $.ajax({url: "struct",
            dataType: 'json',
            data: {format: "json"},
            success: startcode ,
        });
    }
);
