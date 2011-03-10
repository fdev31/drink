sortable = null;
child_items = {};
var url_regex = /^(\/|http).+/;

function startcode(data, status, req) {

   // handle sortables
    sortable.sortable({
        cursor: 'move',
        distance: 5,
        accept: '.entry',
        tolerence: 'pointer',
        helper: 'original',
        revert: true,
        stop: function(event, ui) {
            if ( event.ctrlKey ) {
                var pat = $('#main_list').find('li').map( function() { return $(this).data('item') } ).get().join('/');
                $.post('move', {'set': pat});
                return true;
            } else {
                return false;
            }
        },
    });
   // list-item creation fonction

   for(n=0; n<data.items.length; n++) {
        sortable.add_entry(data.items[n]);
   }

    // Integration of http://valums.com/ajax-upload/
    try {
        qq.UploadDropZone.prototype._isValidFileDrag = function(e){ return true; }
        var uploader = new qq.FileUploader({
            element: $('#file-uploader')[0],
            action: 'upload',
            debug: true,
            showMessage: function(message){ alert(message); },
            onComplete: function(id, fileName, data){
                if ( data.id ) {
                    sortable.add_entry(data);
                }
                $('ul.qq-upload-list > li.qq-upload-success').fadeOut('slow', function() {
                    $(this).remove()
                    });
            },
        });
    } catch (ReferenceError) {
        //console.log('Uploader code not available');
    }


} // End of startup code

$.fn.extend({
    add_entry: function(data) {
        var e = make_li(data)
        sortable.append(e);
        $('#edit_form select').append(
            '<option value="'+data.id+'" label="'+data.id+'">'+data.id+'</option>'
        );
        child_items[data.id] = data;
        e.hide();
        e.fadeIn('slow');
        return e;
    },
    remove_entry: function(item) {
        $.ajax({
            url:'rm?name='+encodeURI(item),
        }).success(function() {
            var safe_name = item.replace( /"/g, '\\"');
            $('#edit_form select option[value="'+safe_name+'"]').remove();
            $('#rm_form select option[value="'+safe_name+'"]').remove();
            $('#rm_form select option[value="'+safe_name+'"]').remove();
            $('ul > li.entry:data(item='+item+')').slideUp('slow', function() {$(this).remove()});
            delete child_items[item];
        }).error(function(){alert('Error removing "'+item+'"')});

    }
});

function make_li(obj) {
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

    var e = $('<li class="entry"><img width="32px" src="'+mime+'" /><a class="item_name" href="'+encodeURI(obj.path+obj.id)+'/" title="'+obj.description+'">'+(obj.title || obj.id)+'</a></li>');
    e.data('item', obj.id);
    e.disableSelection();
	e.dblclick(enter_edit_func);
	e.hover(popup_actions);
	$.ajax({url: obj.path+obj.id+"/struct", context: e,  dataType: "text json"}).success(got_item_details);
    return e;
}
// called whenever make_li is called
// (prints the number of items)
function got_item_details(obj) {
    if (!! $(this).has('.infos') ) {
        if (obj.items.length == 0) {
        } else if (obj.items.length == 1) {
            $(this).append($('&nbsp;<span class="infos">(1 item)</span>'))
        } else {
            $(this).append($('&nbsp;<span class="infos">('+obj.items.length+' items)</span>'))
        }
    }
}

function popup_actions(event) {
    if (event.type == "mouseenter") {
        var me = $(this);
        if ( me.data('edit_called') ) {
            return;
        }

        var elt = child_items[me.data('item')];
        if(!elt._perm.match(/w/)) { return; }

        $(this).data('edit_called', setTimeout(function() {
            var item_name = me.data('item');
            var edit_span = $('<span class="actions"></span>');
            edit_span.append('<a title="Edit" href="./'+encodeURI(item_name)+'/edit"><img class="minicon" src="/static/actions/edit.png" /></a>');
            edit_span.append('<a title="Delete" onclick="sortable.remove_entry(\''+item_name+'\')" ><img class="minicon" src="/static/actions/delete.png" /></a>');
            edit_span.fadeIn('slow');
            me.append(edit_span);

            }, 500));
    } else if (event.type == "mouseleave") {
        clearTimeout($(this).data('edit_called'));
        $(this).data('edit_called', false);
        $(this).find('.actions').fadeOut('slow', function() {$(this).remove()});
    }
}

// handle inline title edition
function blur_on_validate(e) {
    if (e.keyCode == 27) {
         $(this).data('canceled', true);
         $(this).trigger('blur');
    } else if (e.keyCode == 13) {
         $(this).trigger('blur');
    }

}
function exit_edit_func() {
    var txt = null;
	uid = $(this).parent().data('item');
	if (uid == undefined ) { return; }

    if ( $(this).data('canceled') != true && $(this).val() != $(this).data('orig_text') ) {
        txt = $(this).val().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
	    $.post(''+encodeURI(uid)+'/edit', {title: txt} );
    } else {
        txt = $(this).data('orig_text');
    }

	$(this).replaceWith($('<a class="item_name" href="./'+encodeURI(uid)+'/">'+txt+'</a>'));
	$(this).parent().dblclick(enter_edit_func);
}

function enter_edit_func(){
    var elt = child_items[$(this).data('item')];
    if(!elt._perm.match(/w/)) { return; }
    if ( $(this).has('input').length != 0 ) { return; }

    var orig = $(this).find('a.item_name').first();
	// set an input field up, with focus
    var inp = $("<input class=\"inline_edit\" value='"+orig.text()+"' />");
    inp.data('orig_text', orig.text());

    // replace second children
    orig.replaceWith(inp);
	inp = $(this).find("input");
    inp.select();

    // on entry input blur
    inp.blur(exit_edit_func)

    // trigger blur on ENTER keyup
    inp.keyup(blur_on_validate);
}

function fetch_content() {
    sortable = $("#main_list");
    $.ajax({url: "struct", dataType: "text json"}).success(startcode);
}

$(document).ready(fetch_content);
