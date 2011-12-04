// globals
debug = false;

var Page = function () {
    this.classes = [];
    this._perm = 'r';
    this.description = '';
    this.id = '?';
    this.items = [];
    this.mime = "none";
    this.path = "/";
    this.logged_in = false;
    this.title = "unk";
    return this;
}

page_struct = new Page()

url_regex = /^(\/|http).+/;
base_uri = document.location.href.replace(/[^/]*$/, '');
base_path = base_uri.replace(/http?:\/\/[^/]*/, '');

make_std_item = function(data) {
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
    return $('<li class="entry"><img width="32px" src="'+mime+'" /><a class="item_name" href="'+data.path+data.id+'/" title="'+data.description+'">'+(data.title || data.id)+'</a></li>');
}

var Position = function(default_pos, list_getter, selection_class) {
    this.position = default_pos;
    this.lists = list_getter; /* name: children css_selector */
    this.current_list = list_getter[0];
    this.current_list_pos = 0;
    this.selection_class = selection_class;
    this.wrap = true;

    this._select = function() {
        l = this.current_list[1];
        if ( typeof(l) == "string" ) {
            l = $(l);
        } else /* function */ {
            l = l();
        }
        return l;
    }
    this.clear = function() {
        $(l[this.position]).removeClass(this.selection_class);
        this.current_list_pos = 0;
        this.current_list = this.lists[0];
        this.position = 0;
        this.highlight( this._select()[0] );
    }
    this.selected_link = function() {
        var m = this.selected_item();
        if (m.attr('href')) {
            return m.attr('href');
        } else if (m.attr('onclick')) {
            return 'js:'+m.attr('onclick');
        } else if (m.find('a:first').attr('href')) {
            return m.find('a:first').attr('href');
        } else if (m.find('.action:first').attr('onclick')) {
            return 'js:'+m.find('.action:first').attr('onclick');
        } else if (m.find('input:first')) {
            return m.find('input:first');
        } else if (m.find('select:first')) {
            return m.find('select:first');
        } else if (m.find('.input:first')) {
            return m.find('.input:first');
        };
    }
    this.selected_item = function() {
        return $(this._select()[this.position]);
    }
    this.next = function() {
        l = this._select();
        if (this.position < l.length-1) {
            $(l.get(this.position)).removeClass(this.selection_class)
            this.position += 1;
            this.highlight( l[this.position] );
            this.select_next();
        } else if (this.lists[this.lists.length-1][0] != this.current_list[0]) {
            try {
                $(l.get(this.position)).removeClass(this.selection_class)
            } catch (typeError) {
            }
            this.current_list_pos += 1;
            this.current_list = this.lists[this.current_list_pos];
            this.highlight( this._select()[0] );
            this.position = 0;
        } else { /* end of the cycle */
            this.clear();
        }
    }
    this.prev = function() {
        l = this._select();
        if (this.position > 0) {
            $(l.get(this.position)).removeClass(this.selection_class)
            this.position -= 1;
            this.select_prev();
            this.highlight( l[this.position] );
        } else if (this.lists[0][0] != this.current_list[0]) {
            $(l.get(this.position)).removeClass(this.selection_class);
            this.current_list_pos -= 1;
            this.current_list = this.lists[this.current_list_pos];
            this.highlight( this._select()[this.position] );
            this.position = 0;
        } else { /* end of the cycle */
            $(l[this.position]).removeClass(this.selection_class);
            this.current_list_pos = this.lists.length-1;
            this.current_list = this.lists[this.current_list_pos];
            this.position = 0;
            this.highlight( this._select()[0] );
        }
    }
    this.highlight = function(item) {
        var item = $(item);
        item.addClass(this.selection_class)
        item.focus();
        item.center();
    };
    this.select_prev = $.noop;
    this.select_next = $.noop;
    return this;
}
ui = new Object({
        dialog: function(body, buttons, style) {
            var d = $(body);
            d.dialog({
                modal: true,
                closeOnEscape: true,
                buttons: buttons,
                width: '50%',
            });
            if (style == 'big') {
                d.css('width', '100%');
                d.css('padding', '0');
                d.css('margin', 'auto');
                d.css('height', '66%');
            }
            dom_initialize(d);
            return d;
        },
        load_action_list: function(data) {

            if ( !data || !data.actions && !data.types  )  {
                $('#header_bar').slideUp();
                return;
            }
            var pa = $('#page_actions');
            var html = [];

            data = data.actions;

            for (i=0 ; i<data.length ; i++) {
                elt = data[i];
                if (typeof(elt) == "string") {
                    var text=elt;
                } else {
                    // if condition validated & write operations allowed
                    if (
                        (!elt.condition || eval(elt.condition) )
                        &&
                        (page_struct._perm.match('w') || page_struct._perm.match(elt.perm))
                        ) {
                        // if plain link
                        if (elt.action.match(/^[a-zA-Z0-9/]+$/)) {
                            if(!!elt.action.match(/\/$/)) {
                                var text='<a class="action '+(elt.style || '')+'"  title="'+elt.title+'" href="'+elt.action+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
                            } else {
                                var text='<a class="action '+(elt.style || '')+'"  title="'+elt.title+'" href="'+base_uri+elt.action+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
                            }
                        } else { // javascript code
                          var text='<a class="action '+(elt.style || '')+'" title="'+elt.title+'" onclick="'+elt.action+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
                          if (elt.key)
                            keys.add(elt.key, elt.action);
                        };
                    } else {
                        var text=null;
                    }
                };
                if ( text ) { html.push(text); };
            }

            pa.html(html.join(''));
            dom_initialize( pa );

            if (data.length == 0) {
                $('#header_bar').slideUp();
            } else {
                setTimeout(function(){ $('#header_bar').slideDown('slow') }, 1000 );
            }
        },
        reload: function() {
            $.ajax({url: 'struct'}).success(ui.main_list.reload).error(function() {ui.dialog('<div title="Error occured">Listing can\'t be loaded :(</div>')});
        },
        // Move
        move_current_page: function() {
            var win = ui.dialog('<div id="move-confirm" title="Do you really want to move this item ?">Please, type destination path:<input id="move-destination" class="completable" complete_type="objpath"></input></div>', {
                Move: function() {
                    $.post($('#move-confirm #move-destination').val()+'/borrow',
                        {'item': base_path},
                        function() {
                            document.location.href = $('#move-confirm #move-destination').val();
                    }).error(function(){
                        ui.dialog('<div title="Error occured">Sorry, something didn\'t work correctly</div>');
                   });
                },
                Cancel: function() {
                    $( this ).dialog( "close" );
                },
            });
        },
        // EDIT
        edit_entry: function(data) {
           ui.dialog('<iframe title="Edit object" src="'+base_uri+'/'+data+'/edit?embedded=1">No iframe support :(</iframe>', buttons=null, style='big');

        },
        // REMOVE
        remove_entry: function(item) {
            ui.dialog('<div id="remove-confirm" title="Do you really want to remove this item ?">Please, confirm removal.</div>', {
                Accept: function() {
                    $( this ).dialog( "close" );
                    $.ajax({
                        url:'rm?name='+encodeURI(item),
                    }).success(function() {
                        var safe_name = item.replace( /"/g, '\\"');
/*
                        $('#edit_form select option[value="'+safe_name+'"]').remove();
                        $('#rm_form select option[value="'+safe_name+'"]').remove();
                        $('#rm_form select option[value="'+safe_name+'"]').remove();
*/
                        $('ul > li.entry:data(item='+item+')').slideUp('slow', function() {$(this).remove()});
                        delete ui.child_items[item];
                    }).error(function(){
                        $('<div title="Error occured">Sorry, something didn\'t work correctly</div>').dialog();
                       });
                },
                Cancel: function() {
                    $( this ).dialog( "close" );
                }
        });
    },
    current_focus: new Position(-1, [
        ['actions',  '#commands a.action'],
        ['items', 'ul li.entry'],
    ], 'highlighted'),

    child_items: [],
    }
);

// KEYPRESS THINGS
var KeyHandler = function() {
    this.hooks = [];
    this.k = {
        BACK: 8,
        ENTER: 13,
        ESC: 27,
        UP: 38,
        LEFT: 37,
        RIGHT: 39,
        DOWN: 40,
        INS: 45,
        DEL: 46,
    };

    for (i=65; i<=90; i++) {
        this.k[String.fromCharCode(i)] = i;
    };
    this.add = function(key, code) {
        var kcode = this.k[key];
        if (kcode) {
            if (debug && this.hooks[kcode]) {
                alert('Duplicate handler for "'+key+'" key!');
            }
            this.hooks[kcode] = code;
        } else {
            alert("Unknown keycode: "+key);
        }
    };
    this.call = function(e) {
        var tag = e.target.tagName;
        if (!e.ctrlKey && !e.altKey && !e.shiftKey && tag != 'INPUT' && tag != 'TEXTAREA' && tag != 'SELECT') {
           var code = keys.hooks[e.which];
           if (!code) {
               code = keys.hooks[String.fromCharCode(e.which)];
            }
           if (code) {
                try {
                    if (typeof(code) == 'string') {
                        eval(code);
                    } else {
                        code(e);
                    }
                } catch (x) {
                    if(debug) {console.log(code) ; console.log(x); };
                };
                if (debug) console.log('handled '+e.which);
                return false;
            } else {
                if (debug) ui.message("Don't know how to handle"+e);
            }
        }
    };
    return this;
}

keys = new KeyHandler();

// REMOVE ITEM THINGS

remove_item_hooks = [];

function add_hook_remove_item(o) { remove_item_hooks.push(o) }

function call_hook_remove_item(o) {
   for(i=0; i<remove__hooks.length; i++) {
        remove_item_hooks[i](data);
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

        var elt = ui.child_items[me.data('item')];
        if (!elt) return;
        if(!elt._perm.match(/w/)) { return; }

        $(this).data('edit_called', setTimeout(function() {
            var item_name = me.data('item');
            var edit_span = $('<span class="actions"></span>');
            edit_span.append('<a title="Edit" onclick="ui.edit_entry(\''+item_name+'\')"><img class="minicon" src="/static/actions/edit.png" /></a>');
            edit_span.append('<a title="Delete" onclick="ui.remove_entry(\''+item_name+'\')" ><img class="minicon" src="/static/actions/delete.png" /></a>');
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
    var elt = ui.child_items[$(this).data('item')];
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

function dom_initialize(dom) {
    // sumbit forms on Ctrl+Enter press
    dom.find('#auto_edit_form').keypress( function(ev, elt) {
        if ( ev.ctrlKey && ev.charCode == 10 ) {
            $(this).submit();
            return true;
        };
    });
    dom.find('input.completable[complete_type=objpath]').keyup(function(e) {
        if (1 ||debug) { console.log('match'); console.log(e) };
        var o = $(this);
        if (e.which == 13) {
            o.parent().parent().find('button:first').trigger('click');
        }
        if (e.which < 64 && e.which != 17 && e.which != 32 && e.which != 16) return;
        get_matching_elts(o.val(), function(items, path) {
                    o.parent().find('.completed').remove();
                    if (items.length > 1) {
                        var list = items.join('</li><li>');
                        $('<ul class="completed"><li>' + list + '</li></ul>').insertAfter(o);
                    } else {
                        if (items.length == 1 ) {
                            var best_match = items[0];
                            var components = path.split(/\//);
                            if ( components && components[components.length-1] != '' ) {
                                components.pop();
                            };
                            components.push(best_match);
                            components.push('');
                            o.val(components.join('/'));
                        }
                    };
            }
        );
    });

    // change style of checkboxes titles in editable spans form
    dom.find('.editable span').click( function() {
        var o = $(this).prev();
        if ( ! o.is(':checked') ) {
            o.attr('checked', true);
            $(this).addClass('selected', 1000);
        } else {
            o.attr('checked', false);
            $(this).removeClass('selected', 1000);
        }
    });

    // drop edit form's droppable, FIXME: is this code executed ?
    dom.find('.edit_form').droppable({
        drop: function(event, ui) {
            if(debug) console.log('This code is executed #343 drop');
            $(this).removeClass("selected");
    		$($(this)[0][0]).val(ui.draggable.data('item').replace(/&/g, '%26').replace(/\?/g, '%3f'));
            $(this).attr("action", ui.draggable.data('item')+"/edit");
	        $(this).submit();
        },
        over: function(event, ui) {
            if(debug) console.log('This code is executed #343 over');
            $(this).addClass('selected');
        },
        out: function(event, ui) {
            if(debug) console.log('This code is executed #343 out');
            $(this).removeClass("selected");
        }
    });

    // the old rm_form was droppable, FIXME: replace with a trash icon or something
    dom.find('.rm_form').droppable({
        drop: function(event, ui) {
            var item = ui.draggable.data('item');
            $(this).removeClass("selected");
	        ui.remove_entry(ui.draggable.remove());
	        ui.draggable.remove();
        },
        over: function(event, ui) {
            $(this).addClass('selected');
        },
        out: function(event, ui) {
            $(this).removeClass("selected");
        }
    });

    // automatic settings for some special classes
    dom.find('.editable span').addClass('toggler');

    // setup some behaviors

    dom.find(".autovalidate").each(function(index, ob) { $(ob).validate() } );

    dom.find('.auto_date').datepicker({dateFormat: "dd/mm/yy"});

} // dom_initialize


// Helper function to complete valid object path's

function get_matching_elts(path_elt, callback) {
    if (path_elt.match('/')) {
        var _elts = path_elt.split('/');
        _elts.filter(function(e) { if (!!e) return true; });
        url = [document.location.origin];
        for (n=0;n<_elts.length;n++) {
            if (n == _elts.length-1) {
                pattern = _elts[n];
            } else {
                url.push(_elts[n]);
            }
        }
        url.push("/match?pattern=" + pattern);
        url = url.join('/');
    } else {
        pattern  = path_elt;
        url = base_uri + "match?pattern=" + pattern;
    };
    var cur_path = path_elt;
    // AJAX URL
    $.get(url).success(function(data) { callback(data.items, cur_path) } );
}

MainList = function(id) {
    this.id = id || "main_list";
    var me = this;

    this.list = $('#'+this.id);
    this.list.sortable({
        cursor: 'move',
        distance: 5,
        accept: '.entry',
        tolerence: 'pointer',
        helper: 'original',
        revert: true,
        stop: function(event, ui) {
            if ( event.ctrlKey ) {
                var pat = $('#'+this.id+' li').map( function() { return $(this).data('item') } ).get().join('/');
                $.post('move', {'set': pat});
                return true;
            } else {
                return false;
            }
        },
    });

    if ($('#'+this.id).length == 0) {
        if (debug) console.log('No list with name '+this.id);
    }

    // ITEM LIST LOADING THINGS
    this.reload = function(data, status, req) {
            
        // TODO: return actions in struct
        $.ajax({url: 'actions'}).success(ui.load_action_list).error(function() { $('<div title="Error occured">List of actions failed to load</div>').dialog({closeOnEscape:true});});

            if(debug) console.log(data);
            if (!data._perm) return;

            $.extend(page_struct, data);

            if ('' != me.list.html()) {
                me.list.html('');
            }

            // init hooks
            add_hook_add_item(function(data) { ui.main_list.add_entry(data).center() });

           // list-item creation fonction

           for(n=0; n<data.items.length; n++) {
                ui.main_list.add_entry(data.items[n]);
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
                                ui.main_list.add_entry(data);
                            }
                            $('ul.qq-upload-list > li.qq-upload-success').fadeOut('slow', function() {
                                $(this).remove()
                                });
                        },
                    });
                } catch (ReferenceError) {
                    //console.log('Uploader code not available');
                }
            };
        dom_initialize( me.list );
    };
    // ADD an entry
    this.new_entry_dialog = function() {
         if ( page_struct.classes.length < 1 ) {
            w = $('<div title="Ooops!">Nothing can be added here, sorry</div>').dialog({closeOnEscape:true});
            setTimeout(function(){w.fadeOut(function(){w.dialog('close')})}, 2000);
            return;
         };
        var template = '<div id="new_obj_form"  title="New item informations"><select class="obj_class" class="required" name="class"><option value="" label="Select one item type">Select one item type</option>';
        var tpl_ftr = '</select><div class="obj_name"><label for="new_obj_name">Name</label><input id="new_obj_name" type="text" name="name" class="obj_name required identifier" minlength="2" /></div></div>';
        for (t=0; t<page_struct.classes.length; t++) {
            template += '<option value="{0}" label="{0}">{0}</option>'.replace(/\{0\}/g, page_struct.classes[t]);
        }

        var new_obj = $(template+tpl_ftr);

        var check_fn = function(e) {
            if (e.keyCode == 13) {
                validate_fn();
            }
        }
        var validate_fn = function() {
            new_obj.dialog("close");
            var item = {
                'class': new_obj.find('.obj_class').val(),
                'name': new_obj.find('input.obj_name').val(),
            };
            $.post('add', item, call_hook_add_item);
        }

        new_obj.find('input.obj_name').keyup(check_fn);

        new_obj.dialog({
            closeOnEscape:true,
            modal: true,
            buttons: [ {text: 'OK', click: validate_fn} ],
        });

        if (page_struct.classes.length == 1) {
            new_obj.find(".obj_class").val(page_struct.classes[0]).attr('disabled', true);
            new_obj.find('input.obj_name').trigger('click').focus();
        }
    };
        // ADD
    this.add_entry = function(data) {
        var e = eval(page_struct.items_factory.build)(data);
        e.data('item', data.id);
        e.disableSelection();
        if (page_struct.items_factory.click) {
            e.click(eval(page_struct.items_factory.click));
        } else if (page_struct.items_factory.dblclick) {
            e.dblclick(eval(page_struct.items_factory.dblclick));
        }
        if (page_struct.items_factory.hover) {
            e.hover(eval(page_struct.items_factory.hover));
        }
        if ( !! data._nb_items ) {
            if ( data._nb_items == 1 ) {
                e.append($('&nbsp;<span class="infos">(1 item)</span>'));
            } else {
                e.append($('&nbsp;<span class="infos">('+data._nb_items+' items)</span>'));
            }
        }

        // Html is element is prepared, now inject it

        ui.main_list.list.append(e);
        $('#edit_form select').append(
            '<option value="'+data.id+'" label="'+data.id+'">'+data.id+'</option>'
        );
        ui.child_items[data.id] = data;
        e.hide();
        e.fadeIn('slow');
        return e;
    };
    return this;
}

/////// INIT/STARTUP STUFF

$(document).ready(function(){
    // hides some things by default
    $('.starts_hidden').slideUp(0);

    // some globals
    ui.main_list = new MainList();

    // add global methods
    $.fn.extend({
        center: function() {
            $('html,body').animate({
                scrollTop : $(this).offset().top - ($(window).height()/2),
                }, 100); }
        }
    );

    // extend validator (forms)

    $.validator.addMethod("identifier", function(value, element) {
        return this.optional(element) || !/^[._$%/][$%/]*/i.test(value);
    }, 'No "$", "%" or "/" and don\' start with a dot or an underscore, please :)');

    // Hook all keypresses in window
    $(document).bind('keydown', null, keys.call);

    // load main content
    ui.reload();

    // init keys
    // Some shortcuts
    keys.add('DOWN', function() {
        ui.current_focus.next();
    });
    keys.add('UP', function() {
        ui.current_focus.prev();
    });
    keys.add('ENTER', function() {
        var link = ui.current_focus.selected_link();
        if(debug) console.log(link);
        if (typeof(link) == 'string') {
            m = link.match(/^js: *(.*?) *$/);
            if (m) {
                eval(m[1]);
            } else {
                window.location = link;
            }
        } else {
            link.focus();
            link.trigger('click');
        }
    });
    keys.add('DEL', function() {
        ui.remove_entry( ui.current_focus.selected_item().data('item') );
    });
    keys.add('BACK', function() {
        if (window.location.href != base_uri) {
            window.location = base_uri;
        } else {
            window.location = base_uri+'../';
        }
    });
    keys.add('S', function() {
        // focus first entry
        $("input:text:visible:first").focus().center();
    });
    keys.add('E', function() {
        window.location = base_uri+'edit';
    });
    keys.add('ESC', function() {
        ui.current_focus.clear();
    });
    keys.add('L', function() {
        window.location = base_uri+'list';
    });
    keys.add('V', function() {
        window.location = base_uri+'view';
    });
    keys.add('H', function() {
        $('<div title="Keyboard shortcuts"><ul><li>[E]dit</li><li>[S]earch / [S]elect first input field</li><li>[L]ist</li><li>[V]iew</li><li>BACKSPACE: one level up</li><li>UP/DOWN: change selection</li><li>[DEL]ete</li><li>[ENTER]</li><li>ESCAPE: close dialogs</li></ul></div>').dialog({width: '40ex', closeOnEscape: true});
    });

    dom_initialize($(document));
// end of statup code
});
