// globals

Keys = {
    BACK: 8,
    ENTER: 13,
    UP: 38,
    LEFT: 37,
    RIGHT: 39,
    DOWN: 40,
    INS: 45,
    DEL: 46,
};

for (i=65; i<=90; i++) {
    Keys[String.fromCharCode(i)] = i;
};

debug = true;
item_types = [];
page_struct = {_perm : 'r'};
sortable = null;
child_items = {};
current_index = -1;
url_regex = /^(\/|http).+/;
base_uri = document.location.href.replace(/[^/]*$/, '');


$.validator.addMethod("identifier", function(value, element) {
    return this.optional(element) || !/^[._$%/][$%/]*/i.test(value);
}, 'No "$", "%" or "/" and don\' start with a dot or an underscore, please :)');

// KEYPRESS THINGS

keyup_hooks = new Object();

function call_hook_keyup(e) {
    var tag = e.target.tagName;
    if (tag != 'INPUT' && tag != 'TEXTAREA') {
       var code = keyup_hooks[e.which];
       if (!code) {
           code = keyup_hooks[String.fromCharCode(e.which)];
       };
       if (code) {
            try {
                if (typeof(code) == 'string') {
                    eval(code);
                } else {
                    code(e);
                }
            } catch (x) {
                if(debug) console.log(x);
            };
            if (debug) console.log('handled '+e.which);
//            e.preventDefault();
//            e.stopPropagation();
//            document.activeElement.blur();
            return false;
       } else {
            if (debug) console.log('nothing to handle for '+e.which);
            return true;
       }
   }
}

function add_shortcut(key, code) {
    var kcode = Keys[key];
    if (kcode) {
        if (keyup_hooks[kcode]) alert('Duplicate handler for "'+key+'" key!');
        keyup_hooks[kcode] = code;
    } else {
        alert("Unknown keycode: "+key);
    }
}


// ADD ITEM THINGS

add_item_hooks = [];

function add_hook_add_item(o) { add_item_hooks.push(o) }

function call_hook_add_item(data) {
   for(i=0; i<add_item_hooks.length; i++) {
        add_item_hooks[i](data);
   }
}

// Popup actions for items

function popup_actions(event) {
    if (event.type == "mouseenter") {
        var me = $(this);
        if ( me.data('edit_called') ) {
            return;
        }

        var elt = child_items[me.data('item')];
        if (!elt) return;
        if(!elt._perm.match(/w/)) { return; }

        $(this).data('edit_called', setTimeout(function() {
            var item_name = me.data('item');
            var edit_span = $('<span class="actions"></span>');
            edit_span.append('<a title="Edit" onclick="$.edit_entry(\''+item_name+'\')"><img class="minicon" src="/static/actions/edit.png" /></a>');
            edit_span.append('<a title="Delete" onclick="$.remove_entry(\''+item_name+'\')" ><img class="minicon" src="/static/actions/delete.png" /></a>');
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

function enter_edit_func() {
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

// ITEM LIST LOADING THINGS

function refresh_item_list(data, status, req) {
    $.ajax({url: 'actions'}).success(refresh_action_list).error(function() { $('<div title="Error occured">List of actions failed to load</div>').dialog();});

    if (!data._perm) return;

    page_struct = data;

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
                var pat = $('#main_list li').map( function() { return $(this).data('item') } ).get().join('/');
                $.post('move', {'set': pat});
                return true;
            } else {
                return false;
            }
        },
    });

    if ('' != sortable.html()) {
        sortable.html('');
    }

    // init hooks
    add_hook_add_item(sortable.add_entry);

    // init keys
    add_shortcut('S', function() {
        // focus first entry
        $("input:text:visible:first").focus().center();
    })
    add_shortcut('UP', function() {
        if (current_index > 0) {
            $($('ul > li.entry')[current_index].children[0]).removeClass('highlighted');
            current_index -= 1;
            var n = $($('ul > li.entry')[current_index].children[0]);
            n.addClass('highlighted');
            n.trigger('click');
            n.center();
        }
    })
    add_shortcut('DOWN', function() {
        if (current_index < $('ul > li.entry').length - 1) {
            if (current_index >= 0) {
                $($('ul > li.entry')[current_index].children[0]).removeClass('highlighted');
            }
            current_index += 1;
            var n = $($('ul > li.entry')[current_index].children[0]);
            n.addClass('highlighted')
            n.focus();
            n.trigger('click');
            n.center();
        }
    });
    add_shortcut('ENTER', function() {
        if (current_index > -1) {
            window.location = $($('ul > li.entry > a')[current_index]).attr('href');
        }
    });
    add_shortcut('BACK', function() {
        window.location = base_uri+'../';
    });
    add_shortcut('E', function() {
        window.location = base_uri+'edit';
    });
    add_shortcut('L', function() {
        window.location = base_uri+'list';
    });
    add_shortcut('V', function() {
        window.location = base_uri+'view';
    });
   // list-item creation fonction

   for(n=0; n<data.items.length; n++) {
        sortable.add_entry(data.items[n]);
   }

    if ( page_struct._perm.match(/a/) ) {
        // Integration of http://valums.com/ajax-upload/
        try {
            qq.UploadDropZone.prototype._isValidFileDrag = function(e){ return true; }
            var uploader = new qq.FileUploader({
                element: $('#file-uploader')[0],
                action: 'upload',
                //debug: true,
                showMessage: function(message){ $('<div title="Drop zone">'+message+'</div>'); },
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
    }
} // End of sortable startup code

// ACTIONS Loading things

function refresh_action_list(data) {

    if ( !data || !data.actions && !data.types  )  return;

    if (data.length == 0) {
        $('fieldset.toggler').fadeOut();
    } else {
        $('fieldset.toggler').fadeIn();
    }

    item_types = data.types;
    data = data.actions;
    var pa = $('#page_actions');
    var html = [];

    for (i=0 ; i<data.length ; i++) {
        elt = data[i];
        if (typeof(elt) == "string") {
            var text=elt;
        } else {
            if (page_struct._perm.match('w') || page_struct._perm.match(elt.perm)) {
                if (elt.href) {
                  var text='<a title="'+elt.title+'" href="'+base_uri+elt.href+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
                } else {
                  var text='<a title="'+elt.title+'" onclick="'+elt.onclick+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
                  if (elt.key)
                    add_shortcut(elt.key, elt.onclick);
                };
            } else {
                var text=null;
            }
        };
        if ( text ) { html.push(text); };
    }
    $('#page_actions').html(html.join(''));
};

// Helper function to complete valid object path's

function get_matching_elts(path_elt, callback) {
    if (path_elt.match('/')) {
        var _elts = path_elt.split('/');
        _elts.filter(function(e) { if (!!e) return true; });
        for (n=0;n<_elts.length;n++) {
            if (n == _elts.length-1) {
                pattern = _elts[n];
            } else {
                url = _elts[n];
            }
        }
        url = url + "match?pattern=" + pattern;
    } else {
        pattern  = path_elt;
        url = document.location.pathname + "match?pattern=" + pattern;
    };
    // AJAX URL
    $.get(url).success(function(data) { callback(data.items) } );
}

/////// INIT/STARTUP STUFF

$(document).ready(function(){
    // some globals
    sortable = $("#main_list");
    // add some features to jQuery
    // sortable
    $.extend(sortable, {

        add_entry: function(data) {

            // builds li element around an item object

            var mime = "";
            if ( data.mime ) {
                if ( data.mime.match( url_regex )) {
                    mime = data.mime;
                } else {
                    mime = "/static/mime/"+data.mime+".png";
                }
            } else {
                mime = "/static/mime/page.png";
            }

            var e = $('<li class="entry"><img width="32px" src="'+mime+'" /><a class="item_name" href="'+data.path+data.id+'/" title="'+data.description+'">'+(data.title || data.id)+'</a></li>');
            e.data('item', data.id);
            e.disableSelection();
	        e.dblclick(enter_edit_func);
	        e.hover(popup_actions);
	        if ( !! data._nb_items ) {
                if ( data._nb_items == 1 ) {
                    e.append($('&nbsp;<span class="infos">(1 item)</span>'));
                } else {
                    e.append($('&nbsp;<span class="infos">('+data._nb_items+' items)</span>'));
	            }
	        }

	        // Html is element is prepared, now inject it

            sortable.append(e);
            $('#edit_form select').append(
                '<option value="'+data.id+'" label="'+data.id+'">'+data.id+'</option>'
            );
            child_items[data.id] = data;
            e.hide();
            e.fadeIn('slow');
            return e;
        },
    });
    $.fn.extend({
        center: function() {
            $(window).scrollTop($(this).offset().top - ($(window).height()/2)) ;
        },
        }
    );

    $.extend({

        reload_all: function() {
            $.ajax({url: 'struct'}).success(refresh_item_list).error(function() {  $('<div title="Error occured">Listing can\'t be loaded :(</div>').dialog();}) ;
        },
        new_entry: function() {
             if ( item_types.length <= 1 ) {
                w = $('<div title="Ooops!">Nothing can be added here, sorry</div>').dialog({closeOnEscape:true});
                setTimeout(function(){w.fadeOut(function(){w.dialog('close')})}, 2000);
                return;
             };
            var template = '<div id="new_obj_form"  title="New item informations"><select class="obj_class" class="required" name="class"><option value="" label="Select one item type">Select one item type</option>';
            var tpl_ftr = '</select><div class="obj_name"><label for="new_obj_name">Name</label><input id="new_obj_name" type="text" name="name" class="required identifier" minlength="2" /></div></div>';
            for (t=0; t<item_types.length; t++) {
                template += '<option value="{0}" label="{0}">{0}</option>'.replace(/\{0\}/g, item_types[t]);
            }

            var new_obj = $(template+tpl_ftr);

            var check_fn = function(e) {
                if (e.keyCode == 27) {
                    new_obj.dialog("close");
                } else if (e.keyCode == 13) {
                    validate_fn();
                }
            }
            var validate_fn = function() {
                new_obj.dialog("close");
                var item = {
                    'class': new_obj.find('.obj_class').val(),
                    'name': new_obj.find('#new_obj_name').val(),
                };
                $.post('add', item, call_hook_add_item);
            }

            new_obj.find('#new_obj_name').keyup(check_fn);

            new_obj.dialog({
                modal: true,
                buttons: [ {text: 'OK', click: validate_fn} ],
            });
        },
        edit_entry: function(data) {
           frame = $('<iframe title="Edit object" src="'+base_uri+'/'+data+'/edit?embedded=1">No iframe support :(</iframe>');
            frame.dialog({modal:true, width:'90%'});
            frame.css('width', '100%');
            frame.css('padding', '0');
            frame.css('margin', 'auto');
            frame.css('height', '66%');
        },
        remove_entry: function(item) {
            $('<div id="remove-confirm" title="Do you really want to remove this item ?">Please, confirm removal.</div>').dialog({
                modal: true,
                buttons: {
                    Accept: function() {
                        $( this ).dialog( "close" );
                        $.ajax({
                            url:'rm?name='+encodeURI(item),
                        }).success(function() {
                            var safe_name = item.replace( /"/g, '\\"');
                            $('#edit_form select option[value="'+safe_name+'"]').remove();
                            $('#rm_form select option[value="'+safe_name+'"]').remove();
                            $('#rm_form select option[value="'+safe_name+'"]').remove();
                            $('ul > li.entry:data(item='+item+')').slideUp('slow', function() {$(this).remove()});
                            delete child_items[item];
                        }).error(function(){
                            $('<div title="Error occured">Sorry, something didn\'t work correctly</div>').dialog();
                           });
                    },
                    Cancel: function() {
                        $( this ).dialog( "close" );
                    }
                }
            });
        }
    });
    // debug mode
    //$.validator.setDefaults({debug: true});

    // setup some behaviors

    $(".autovalidate").each(function(index, ob) { $(ob).validate() } );

    // sumbit forms on Ctrl+Enter press
    $('#auto_edit_form').keypress( function(ev, elt) {
        if ( ev.ctrlKey && ev.charCode == 10 ) {
            $(this).submit();
            return true;
        };
    });

    // change style of checkboxes titles in editable spans form
    $('.editable span').click( function() {
        var o = $(this).prev();
        if ( ! o.is(':checked') ) {
            o.attr('checked', true);
            $(this).addClass('selected', 1000);
        } else {
            o.attr('checked', false);
            $(this).removeClass('selected', 1000);
        }
    });

    // the old rm_form was droppable, FIXME: replace with a trash icon or something
    $('#rm_form').droppable({
        drop: function(event, ui) {
            var item = ui.draggable.data('item');
            $(this).removeClass("selected");
			sortable.remove_entry(ui.draggable.remove());
			ui.draggable.remove();
        },
        over: function(event, ui) {
            $(this).addClass('selected');
        },
		out: function(event, ui) {
		    $(this).removeClass("selected");
		}
    });

    // drop edit form's droppable, FIXME: is this code executed ?
    $('#edit_form').droppable({
        drop: function(event, ui) {
            //console.log('This code is executed #343 drop');
            $(this).removeClass("selected");
    		$($(this)[0][0]).val(ui.draggable.data('item').replace(/&/g, '%26').replace(/\?/g, '%3f'));
            $(this).attr("action", ui.draggable.data('item')+"/edit");
			$(this).submit();
        },
        over: function(event, ui) {

            //console.log('This code is executed #343 over');
            $(this).addClass('selected');
        },
		out: function(event, ui) {

            //console.log('This code is executed #343 out');
		    $(this).removeClass("selected");
		}
    });

    // automatic settings for some special classes
    $('.editable span').addClass('toggler');
    $('.auto_date').datepicker({dateFormat: "dd/mm/yy"});

    // Hook all keypresses in window
    $('body').bind('keydown', null, call_hook_keyup );

    // load main content
    $.reload_all();

});
