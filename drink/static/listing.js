var startcode = function(data, status, req) {
   var sortable = $(".sortable");
   data.items.length;
   sortable.data('items', data.items)
   sortable.html('');
   var i;
   var url_regex = /^(\/|http).+/;

   var make_li = function (obj) {
        var mime = "";
        if ( obj.mime ) {
            if ( obj.mime.match( url_regex )) {
                mime = obj.mime;
            } else {
                mime = "/static/mime/"+obj.mime+".png";
            }
        } else {
            mime = "/static/mime/page.png";
        }

        var e = $('<li class="entry"><img width="32px" src="'+mime+'" /><a href="'+obj.path+obj.id+'/view">'+(obj.title || obj.id)+'</a></li>');
        e.data('item', obj.id);
        e.disableSelection();
        return e;
    }

   for(n=0; n<data.items.length; n++) {
        sortable.append(make_li(data.items[n]));
   }
   sortable.sortable({
//        axis: "y",
//        containment: ".sortable",
        cursor: 'move', update: function(event, ui) {
            var pat = $('.sortable').find('li').map( function() { return $(this).data('item') } ).get().join('/');
            $.post('move', {'set': pat});
        },
   });

    var enter_edit_func = function(){
		txt = $(this).text();
		// set an input field up, with focus
		$(this).html("<input value='"+txt+"' />");
		$(this).find("input").select();
	}

	var exit_edit_func = function(){
		txt = $(this).val().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");;
		uid = $(this).parent().data('item');
		if (uid == undefined) { return; }
		$.post(''+uid+'/edit', {title: txt} );
		// FIXME: set the item display
		var li = make_li({id: uid, title: txt, path: './'});
		li.dblclick(enter_edit_func);
	    li.live('blur', exit_edit_func);
	    li.live('keyup', on_enter);
		$(this).parent().replaceWith(li);
	}

	var on_enter = function(e) {
	    if (e.keyCode == 13) { $(this).trigger('blur'); };
	}

	sortable.find(".entry").dblclick(enter_edit_func)

	// on entry input blur
	sortable.find(".entry input").live("blur", exit_edit_func)

    // trigger blur on ENTER keyup
	sortable.find(".entry input").live("keyup", on_enter);


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
